import json
import logging
from collections import defaultdict
from typing import List, Dict, Any
from app.fingerprint.matcher import matcher
from app.classifier.unknown_classifier import unknown_classifier
from app.scoring.risk_engine import risk_engine

logger = logging.getLogger(__name__)


def parse_extension_inventory(content: str) -> List[Dict[str, Any]]:
    """
    Parses browser extension inventory JSON exports from Chrome / Edge Enterprise Management.
    Detects known AI extensions and unvetted high-risk AI copilot extensions.
    """
    cleaned = content.strip()
    records: List[Dict[str, Any]] = []

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "extensions" in data:
            records = data["extensions"]
        elif isinstance(data, list):
            records = data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding extension inventory JSON: {e}")
        return []

    # Extension Aggregator
    # Key: extension_name -> dict
    aggregated: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "name": "",
        "extension_id": "",
        "version": "",
        "permissions": set(),
        "users": set(),
        "install_count": 0,
    })

    for row in records:
        name = row.get("name") or row.get("title") or row.get("extension_name") or ""
        if not name:
            continue

        ext_id = row.get("extension_id") or row.get("id") or ""
        user = row.get("user_email") or row.get("user") or "unknown_user"
        perms = row.get("permissions") or []
        if isinstance(perms, str):
            perms = [p.strip() for p in perms.split(",") if p.strip()]

        agg = aggregated[name]
        agg["name"] = name
        if ext_id:
            agg["extension_id"] = ext_id
        agg["users"].add(user)
        agg["permissions"].update(perms)
        agg["install_count"] += 1

    findings_data: List[Dict[str, Any]] = []

    for name, stats in aggregated.items():
        users_count = len(stats["users"])
        install_count = stats["install_count"]
        permissions_list = list(stats["permissions"])

        # Analyze specific Data Loss Prevention (DLP) & Credential leakage risks
        dlp_risks = []
        if "clipboardRead" in permissions_list:
            dlp_risks.append("Clipboard Access (Can read copied passwords & API keys)")
        if any(p in permissions_list for p in ["cookies", "webRequest", "webRequestBlocking"]):
            dlp_risks.append("Network Interception (Can intercept auth cookies & form submissions)")
        if any(p in permissions_list for p in ["<all_urls>", "*://*/*"]):
            dlp_risks.append("Broad Tab Access (Can scrape sensitive internal intranet DOM)")

        # Estimate data exposure based on permission scope & installs
        has_broad_access = len(dlp_risks) > 0
        simulated_bytes = (50000000 if has_broad_access else 5000000) * users_count

        # 1. Match against known Fingerprint DB
        fp_match = matcher.match_extension(name)

        if fp_match:
            category = fp_match.get("category", "AI Browser Copilot")
            vendor = fp_match.get("vendor", "Extension Publisher")
            is_sanctioned = fp_match.get("sanctioned", False)
            sanction_status = "sanctioned" if is_sanctioned else "unsanctioned"

            score, tier, breakdown = risk_engine.calculate(
                category=category,
                sanction_status=sanction_status,
                data_exposure_bytes=simulated_bytes,
                users_affected=users_count,
                event_count=install_count * 10,
            )

            if dlp_risks:
                breakdown["dlp_threat_indicators"] = dlp_risks
                breakdown["explanation"] += f" DLP Risk Factors: {', '.join(dlp_risks)}."

            findings_data.append({
                "entity_type": "extension",
                "entity_value": name,
                "category": category,
                "vendor": vendor,
                "sanction_status": sanction_status,
                "data_exposure_bytes": simulated_bytes,
                "users_affected": users_count,
                "event_count": install_count,
                "risk_score": score,
                "risk_tier": tier,
                "breakdown": breakdown,
            })
        else:
            # 2. Run Unknown Classifier for extensions
            classification = unknown_classifier.classify_extension(name, permissions=permissions_list)

            if classification["is_likely_ai"]:
                category = classification["inferred_category"]
                vendor = "Unvetted Extension Publisher"
                sanction_status = "unknown"

                score, tier, breakdown = risk_engine.calculate(
                    category=category,
                    sanction_status=sanction_status,
                    data_exposure_bytes=simulated_bytes,
                    users_affected=users_count,
                    event_count=install_count * 10,
                )

                if dlp_risks:
                    breakdown["dlp_threat_indicators"] = dlp_risks
                    breakdown["explanation"] += f" DLP Risk Factors: {', '.join(dlp_risks)}."

                findings_data.append({
                    "entity_type": "extension",
                    "entity_value": name,
                    "category": category,
                    "vendor": vendor,
                    "sanction_status": sanction_status,
                    "data_exposure_bytes": simulated_bytes,
                    "users_affected": users_count,
                    "event_count": install_count,
                    "risk_score": score,
                    "risk_tier": tier,
                    "breakdown": breakdown,
                })

    return findings_data
