from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.db import repository
from app.db.models import User, AgentInvestigation
from app.auth.dependencies import require_role
from app.scoring.risk_engine import RiskEngine
from app.agent.investigator_agent import ShadowAIInvestigatorAgent
from app.schemas import FindingResponse, FindingDetailResponse, RiskFactorBreakdown, AgentInvestigationResponse
from app.config import settings

router = APIRouter(prefix="/findings", tags=["Findings"])

risk_engine = RiskEngine(
    w_sensitivity=settings.WEIGHT_CATEGORY_SENSITIVITY,
    w_sanction=settings.WEIGHT_SANCTION_STATUS,
    w_exposure=settings.WEIGHT_DATA_EXPOSURE,
    w_usage=settings.WEIGHT_USAGE_SPREAD
)
investigator_agent = ShadowAIInvestigatorAgent()


@router.get("", response_model=List[FindingResponse])
def get_all_findings(
    scan_id: Optional[str] = None,
    risk_tier: Optional[str] = Query(None, description="Filter by: critical, high, medium, low"),
    sanction_status: Optional[str] = Query(None, description="Filter by: sanctioned, unsanctioned, unknown"),
    entity_type: Optional[str] = Query(None, description="Filter by: domain, extension"),
    category: Optional[str] = Query(None, description="Partial match on category name"),
    search: Optional[str] = Query(None, description="Partial match on entity value or vendor"),
    current_user: User = Depends(require_role("admin", "analyst", "viewer"))
):
    """
    Search and filter across all findings in the system.
    """
    findings = repository.list_findings(
        scan_id=scan_id,
        risk_tier=risk_tier,
        sanction_status=sanction_status,
        entity_type=entity_type,
        category=category,
        search=search
    )
    return [FindingResponse.model_validate(f) for f in findings]


@router.get("/{finding_id}", response_model=FindingDetailResponse)
def get_finding_detail(
    finding_id: str,
    current_user: User = Depends(require_role("admin", "analyst", "viewer"))
):
    """
    Retrieves full details of a specific finding, including its risk score
    breakdown factors and any linked AI investigations.
    """
    finding = repository.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    factors = risk_engine.get_breakdown_factors(
        category=finding.category,
        sanction_status=finding.sanction_status,
        data_exposure_bytes=finding.data_exposure_bytes,
        users_affected=finding.users_affected
    )
    
    breakdown = RiskFactorBreakdown(
        category_risk=factors["category_score"],
        sanction_risk=factors["sanction_score"],
        data_exposure_risk=factors["exposure_score"],
        usage_spread_risk=factors["usage_score"]
    )

    explanation_breakdown = {
        "category_score": factors["category_score"],
        "sanction_score": factors["sanction_score"],
        "data_exposure_score": factors["exposure_score"],
        "usage_spread_score": factors["usage_score"],
        "weights": {
            "category": settings.WEIGHT_CATEGORY_SENSITIVITY,
            "sanction": settings.WEIGHT_SANCTION_STATUS,
            "data_exposure": settings.WEIGHT_DATA_EXPOSURE,
            "usage_spread": settings.WEIGHT_USAGE_SPREAD,
        }
    }

    # Fetch associated investigations
    investigations = repository.get_investigations_for_finding(finding.id)
    inv_responses = [AgentInvestigationResponse.model_validate(inv) for inv in investigations]
    primary_investigation = inv_responses[0] if inv_responses else None

    response_data = finding.model_dump()
    response_data["risk_breakdown"] = breakdown
    response_data["explanation_breakdown"] = explanation_breakdown
    response_data["investigation"] = primary_investigation
    response_data["investigations"] = inv_responses

    return FindingDetailResponse.model_validate(response_data)


@router.post("/{finding_id}/investigate", response_model=AgentInvestigationResponse)
async def investigate_finding_endpoint(
    finding_id: str,
    current_user: User = Depends(require_role("admin", "analyst"))
):
    """
    Triggers LLM Agent triage & investigation for a finding.
    """
    finding = repository.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding_data = finding.model_dump()
    result = await investigator_agent.investigate_finding(finding_data)

    inv = AgentInvestigation(
        finding_id=finding.id,
        summary=result["summary"],
        recommendation=result["recommendation"],
        rationale=result["rationale"],
        confidence=result["confidence"]
    )
    saved_inv = repository.create_agent_investigation(inv)
    return AgentInvestigationResponse.model_validate(saved_inv)
