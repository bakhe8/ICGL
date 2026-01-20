from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from fastapi.encoders import jsonable_encoder
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.dependencies import _require_api_key, logger, get_consensus_service
from api.models.governance import (
    ProposalPayload, ProposalRecord, ProposalUpdate,
    DecisionPayload, ConflictPayload, ConflictUpdate,
    CommitteeRequest, ReportRequest, RequestRequest, DecisionRequest,
    UIReviewRequest, ConflictCaseRequest, SignRequest, ProposalRequest
)
from kb.schemas import ADR, Proposal as ProposalSchema, uid
from api.services.consensus_service import ConsensusService

# Note: We are migrating away from the simplified GovernanceService in favor of the full ConsensusService
# from api.services.governance_service import GovernanceService

router = APIRouter(prefix="/api/governance", tags=["Governance"])

# --- Committee Endpoints ---

@router.post("/committee/add")
async def add_committee(req: CommitteeRequest, _: bool = Depends(_require_api_key)):
    logger.info(f"Adding committee: {req.name}")
    return {"status": "accepted", "id": 123} # Mocked for now

@router.post("/report/add")
async def add_report(req: ReportRequest, _: bool = Depends(_require_api_key)):
    return {"status": "recorded", "id": 456}

# --- Proposal Management ---

def _adr_to_proposal_view(adr: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize ADR records for UI proposal view."""
    return {
        "id": adr.get("id"),
        "title": adr.get("title"),
        "description": adr.get("context") or adr.get("description") or "",
        "reason": adr.get("reason") or adr.get("decision", ""),
        "impact": adr.get("impact") or "",
        "risks": adr.get("risks", ""),
        "state": (adr.get("status") or "PROPOSED").lower(),
        "author": adr.get("author", "operator"),
        "created_at": adr.get("created_at"),
        "updated_at": adr.get("updated_at", adr.get("created_at")),
        "tags": adr.get("tags", []),
        "assigned_agents": adr.get("assigned_agents", []),
        "comments": adr.get("comments", []),
    }

@router.get("/proposals")
async def get_proposals(service: ConsensusService = Depends(get_consensus_service)):
    """List ADR proposals from the Consensus Knowledge Base."""
    adrs = service.adr_repo.get_all()
    return {"proposals": [_adr_to_proposal_view(a) for a in adrs]}

@router.post("/proposals/create")
async def create_proposal(payload: ProposalRequest, service: ConsensusService = Depends(get_consensus_service)):
    """Create a new ADR proposal via ConsensusService."""
    try:
        decision_text = payload.decision
        reason = getattr(payload, "reason", None)
        impact = getattr(payload, "impact", None)
        if reason or impact:
            decision_text = f"Reason: {reason or ''}\nImpact: {impact or ''}\nDecision: {payload.decision}"
        result = service.propose_adr(payload.title, payload.context, decision_text, reason=reason, impact=impact)
        return {"proposal": _adr_to_proposal_view(result)}
    except Exception as e:
        logger.error(f"Error creating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ADR / KB Endpoints ---

@router.get("/kb/list")
async def list_kb(type: str, service: ConsensusService = Depends(get_consensus_service)):
    """List knowledge base entities."""
    if type == "adr": 
        adrs = service.adr_repo.get_all()
        return [_adr_to_proposal_view(a) for a in adrs]
    return []

@router.get("/adr/latest")
async def get_latest_adr(service: ConsensusService = Depends(get_consensus_service), _: bool = Depends(_require_api_key)):
    """Fetch the latest ADR."""
    adr = service.adr_repo.get_latest()
    return _adr_to_proposal_view(adr) if adr else None

@router.post("/adr/{adr_id}/sign")
async def sign_decision(adr_id: str, req: SignRequest, service: ConsensusService = Depends(get_consensus_service)):
    """Sign an ADR decision (Human Authority)."""
    try:
        # SignRequest has 'action' (approvied/rejected) and 'rationale'
        decision = req.action.lower() if hasattr(req, 'action') else "approved"
        result = service.register_decision(
            proposal_id=adr_id,
            decision=decision,
            rationale=req.rationale,
            signed_by=req.human_id
        )
        return {"status": "signed", "adr_id": adr_id, "decision": result}
    except Exception as e:
        logger.error(f"Error signing ADR {adr_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_governance_dashboard(service: ConsensusService = Depends(get_consensus_service)):
    """Aggregates KB status, active proposals, and recorded decisions."""
    try:
        adrs = service.adr_repo.get_all()
        decisions = service.decision_repo.get_all()
        policies = service.policy_repo.get_all()
        
        pending_adrs = [a for a in adrs if (a.get("status") or "").upper() == "PROPOSED"]
        
        return {
            "proposals": {
                "total": len(adrs),
                "pending": len(pending_adrs),
                "active_list": [_adr_to_proposal_view(a) for a in pending_adrs[:5]]
            },
            "decisions": {
                "total": len(decisions),
                "latest": decisions[-1] if decisions else None
            },
            "policies": {
                "total": len(policies)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Decisions ---

@router.get("/decisions")
async def list_decisions(service: ConsensusService = Depends(get_consensus_service)):
    """Return recorded decisions (human/agent votes)."""
    try:
        return {"decisions": service.decision_repo.get_all()}
    except Exception as e:
        logger.error(f"Error listing decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeline")
async def list_governance_timeline():
    """Returns a chronological list of governance events."""
    return {"timeline": []}

@router.get("/conflicts")
async def list_conflicts():
    """Returns unresolved governance conflicts."""
    return {"conflicts": []}

@router.post("/decisions/register")
async def register_decision(payload: DecisionPayload, service: ConsensusService = Depends(get_consensus_service)):
    """Register a decision against an ADR/proposal."""
    try:
        record = service.register_decision(
            proposal_id=payload.proposal_id,
            decision=payload.decision,
            rationale=payload.rationale,
            signed_by=payload.signed_by
        )
        return {"decision": record}
    except Exception as e:
        logger.error(f"Error registering decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))
