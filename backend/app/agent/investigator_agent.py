import json
import logging
import re
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class ShadowAIInvestigatorAgent:
    """
    LLM Agent for Shadow AI Triage and Deep Investigation.
    Synthesizes security findings, category heuristics, and enterprise context
    to return a structured security verdict (block / monitor / escalate).
    """

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL

    async def investigate_finding(
        self,
        finding_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes investigation. If ANTHROPIC_API_KEY is available, calls Claude (claude-sonnet-4-6).
        Otherwise, uses the deterministic contextual analysis engine to return an identical structured verdict.
        """
        if self.api_key and self.api_key.strip() and not self.api_key.startswith("your-"):
            try:
                return await self._call_claude(finding_data, context)
            except Exception as e:
                logger.error(f"Claude API call failed: {e}. Falling back to deterministic contextual triage engine.")
                return self._local_triage_engine(finding_data, context)
        else:
            return self._local_triage_engine(finding_data, context)

    async def _call_claude(
        self,
        finding_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calls Anthropic Claude with strict JSON schema enforcement."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        prompt = f"""You are the Lead Cybersecurity DLP & Threat Triage Agent for "Shadow AI Sentinel".

ORGANIZATIONAL AI POLICY:
- We are supportive of AI adoption, employee innovation, and productivity.
- We DO NOT ban AI tools merely for being AI.
- We STRICTLY PREVENT Data Loss Prevention (DLP) violations—specifically stopping sensitive enterprise data (passwords, API tokens, database credentials, confidential source code, customer PII, financial spreadsheets, and trade secrets) from being exfiltrated to unapproved AI endpoints or intercepted by over-permissioned browser extensions.

FINDING DETAILS:
{json.dumps(finding_data, indent=2)}

ADDITIONAL CONTEXT:
{json.dumps(context or {}, indent=2)}

TASK:
1. Provide a concise technical summary focusing on whether this AI service/extension poses a risk of leaking sensitive enterprise data, passwords, or credentials.
2. Select EXACTLY ONE triage recommendation from:
   - "block" (High/Critical threat of credential leakage, unencrypted secret transmission, unauthorized clipboard/keystroke scraping, or heavy unmonitored payload exfiltration)
   - "monitor" (Legitimate productivity AI tool with safe usage; ensure DLP guidelines and credential safeguards are observed)
   - "escalate" (Suspicious or high-volume data egress where passwords, credentials, or proprietary source code might be exposed)
3. Provide a clear justification (rationale) emphasizing data protection, credential safety, and acceptable use guidelines without unnecessarily restricting employee productivity.
4. Provide a confidence score between 0.50 and 1.00.

MANDATORY OUTPUT FORMAT:
You must output ONLY valid JSON matching this exact structure:
{{
  "summary": "...",
  "recommendation": "block" | "monitor" | "escalate",
  "rationale": "...",
  "confidence": 0.95
}}
"""

        response = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text.strip()
        # Parse JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            return {
                "summary": str(parsed.get("summary", "Analysis completed.")),
                "recommendation": str(parsed.get("recommendation", "monitor")).lower(),
                "rationale": str(parsed.get("rationale", "Standard organizational review recommended.")),
                "confidence": float(parsed.get("confidence", 0.9)),
            }
        else:
            raise ValueError(f"Could not parse valid JSON from Claude response: {content}")

    def _local_triage_engine(
        self,
        finding_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deterministic, DLP-first triage engine used when Anthropic API key is not configured.
        Prioritizes protection against credential leaks, secret exfiltration, and sensitive data loss.
        """
        entity = finding_data.get("entity_value", "Unknown Service")
        entity_type = finding_data.get("entity_type", "domain")
        category = finding_data.get("category", "Generative AI")
        sanction_status = finding_data.get("sanction_status", "unknown").lower()
        risk_score = float(finding_data.get("risk_score", 50.0))
        risk_tier = finding_data.get("risk_tier", "medium").lower()
        bytes_exposed = int(finding_data.get("data_exposure_bytes", 0))
        users_affected = int(finding_data.get("users_affected", 1))

        # Determine Recommendation based on DLP / Credential Exposure Risk
        if risk_tier == "critical" or risk_score >= 80.0:
            recommendation = "block"
            confidence = 0.96
            summary = (
                f"Critical Data Loss & Credential Risk detected on {entity} ({category}). "
                f"High-risk telemetry with {bytes_exposed:,} bytes transmitted across {users_affected} workstation(s). "
                f"This entity exhibits permissions or behaviors capable of scraping active passwords, API tokens, or proprietary IP into external AI servers."
            )
            rationale = (
                f"Immediate perimeter containment recommended. The primary concern is unvetted data exfiltration—employees or extensions "
                f"could inadvertently transmit company passwords, API keys, customer PII, or confidential source code. "
                f"Enforce endpoint DLP policy to safeguard organizational secrets while directing users to enterprise-sanctioned AI portals."
            )
        elif risk_tier == "high" or risk_score >= 60.0:
            if users_affected > 10:
                recommendation = "escalate"
                confidence = 0.92
                summary = (
                    f"{entity} ({category}) is actively utilized by {users_affected} team members for productivity, "
                    f"but lacks verified Data Loss Prevention (DLP) guardrails against credential and secret sharing."
                )
                rationale = (
                    f"Escalate to Information Security. Because employees rely on this tool for productivity, evaluate provisioning "
                    f"an enterprise account equipped with zero-data-retention, credential-masking, and DLP controls rather than a hard block."
                )
            else:
                recommendation = "block"
                confidence = 0.89
                summary = (
                    f"{entity} ({category}) is an unverified {entity_type} presenting potential credential leakage or sensitive payload exposure ({bytes_exposed:,} bytes)."
                )
                rationale = (
                    f"Block unvetted endpoint access and revoke dangerous extension permissions (e.g. clipboard/tab scraping) "
                    f"to prevent accidental leakage of sensitive corporate credentials and internal documents."
                )
        elif sanction_status == "sanctioned":
            recommendation = "monitor"
            confidence = 0.98
            summary = (
                f"{entity} is an approved enterprise AI service ({category}). Safe for employee productivity."
            )
            rationale = (
                f"Maintain continuous telemetry. Verified enterprise AI usage is encouraged; remind team members to avoid pasting "
                f"raw system passwords or production master keys into prompt inputs."
            )
        else:
            recommendation = "monitor"
            confidence = 0.85
            summary = (
                f"{entity} is a productivity AI tool ({category}) with low data volume ({bytes_exposed:,} bytes). "
                f"No immediate credential leakage detected."
            )
            rationale = (
                f"Productivity usage is permitted. Maintain standard DLP monitoring and deliver automated security reminders "
                f"cautioning employees never to input company passwords, credentials, or sensitive customer data."
            )

        return {
            "summary": summary,
            "recommendation": recommendation,
            "rationale": rationale,
            "confidence": confidence,
        }


investigator_agent = ShadowAIInvestigatorAgent()


async def analyze_finding_with_ai(
    finding_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compatibility wrapper function for routes_agent.py.
    """
    return await investigator_agent.investigate_finding(finding_data, context)
