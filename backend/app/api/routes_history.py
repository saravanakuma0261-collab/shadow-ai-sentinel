from fastapi import APIRouter, Depends
from typing import List
from app.db import repository
from app.db.models import User
from app.auth.dependencies import require_role
from app.schemas import DashboardSummaryResponse, ScanHistoryItemResponse, ScanResponse, TopRiskEntity

router = APIRouter(prefix="/history", tags=["Dashboard & History"])


@router.get("/scans", response_model=List[ScanHistoryItemResponse])
def get_scan_history(
    current_user: User = Depends(require_role("admin", "analyst", "viewer"))
):
    """
    Returns a list of all historical scans and the number of findings they generated.
    """
    scans = repository.list_scans()
    
    history = []
    for scan in scans:
        # Need to query counts per scan
        finding_count = repository.count_findings_for_scan(scan.id)
        
        history.append(ScanHistoryItemResponse(
            scan=ScanResponse.model_validate(scan, from_attributes=True),
            total_findings=finding_count
        ))
        
    return history


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(require_role("admin", "analyst", "viewer"))
):
    """
    Returns aggregated metrics for the frontend dashboard widgets.
    """
    # Finding metrics
    total_findings = repository.count_all_findings()
    critical_count = repository.count_findings_by_tier("critical")
    high_count = repository.count_findings_by_tier("high")
    
    # Shadow AI / unsanctioned spread
    unsanctioned_count = repository.count_findings_by_sanction_statuses(["unsanctioned", "unknown"])
    
    # Aggregate data exposure (aggregated in application code)
    total_exposure = repository.sum_findings_field("data_exposure_bytes")

    # Top Risks (Order by score limit 5)
    top_findings = repository.top_findings(limit=5)
    top_risks = [
        TopRiskEntity(
            id=f.id,
            entity_value=f.entity_value,
            risk_score=f.risk_score,
            risk_tier=f.risk_tier,
            category=f.category
        ) for f in top_findings
    ]
    
    # Recent scans (limit 5)
    recent_scans = [
        ScanResponse.model_validate(s, from_attributes=True) 
        for s in repository.list_scans(limit=5)
    ]

    return DashboardSummaryResponse(
        total_findings=total_findings,
        critical_risk_count=critical_count,
        high_risk_count=high_count,
        unsanctioned_apps_count=unsanctioned_count,
        total_data_exposure_bytes=total_exposure,
        top_risks=top_risks,
        recent_scans=recent_scans
    )
