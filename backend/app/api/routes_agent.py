from fastapi import APIRouter, Depends, HTTPException, status
from app.db import repository
from app.db.models import User, AgentInvestigation
from app.auth.dependencies import require_role
from app.agent.investigator_agent import analyze_finding_with_ai
from app.schemas import AgentInvestigationResponse, MessageResponse

router = APIRouter(prefix="/agent", tags=["AI Investigator Agent"])

@router.post("/investigate/{finding_id}", response_model=AgentInvestigationResponse)
async def run_agent_investigation(
    finding_id: str,
    current_user: User = Depends(require_role("admin", "analyst"))
):
    """
    Manually trigger the AI Investigator Agent to analyze a specific finding.
    The agent calls the Anthropic API to analyze the entity, classify its risk,
    and suggest remediation steps.
    """
    finding = repository.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    try:
        # Call the agent logic (which is pure and unchanged)
        result_dict = await analyze_finding_with_ai(finding.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Agent investigation failed: {str(e)}"
        )

    # Save the result to Supabase
    investigation = AgentInvestigation(
        finding_id=finding.id,
        summary=result_dict["summary"],
        recommendation=result_dict["recommendation"],
        rationale=result_dict["rationale"],
        confidence=result_dict["confidence"]
    )
    investigation = repository.create_agent_investigation(investigation)

    return investigation
