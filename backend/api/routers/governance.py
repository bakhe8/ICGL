from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    ADRSummary,
    ConflictsResp,
    DecisionsResp,
    LatestAdrResp,
    OperationResult,
    ProposalResp,
    ProposalsList,
    TimelineResp,
)
from backend.api.server import get_icgl
from shared.python.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/proposals", response_model=ProposalsList)
async def list_proposals(state: str = None) -> ProposalsList:
    try:
        icgl = get_icgl()
        adrs = list(icgl.kb.adrs.values()) if hasattr(icgl, "kb") else []
        if state:
            adrs = [a for a in adrs if getattr(a, "status", "") == state.upper()]
        items = [
            ADRSummary(
                id=getattr(a, "id", None),
                title=getattr(a, "title", None),
                status=getattr(a, "status", None),
                created_at=str(getattr(a, "created_at", None)),
            )
            for a in adrs
        ]
        return ProposalsList(proposals=items)
    except Exception as e:
        logger.error(f"list_proposals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}", response_model=ProposalResp)
async def get_proposal(proposal_id: str) -> ProposalResp:
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(proposal_id) if hasattr(icgl, "kb") else None
        if not adr:
            raise HTTPException(status_code=404, detail="Proposal not found")
        return ProposalResp(proposal=adr.__dict__ if not isinstance(adr, dict) else adr)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_proposal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decisions", response_model=DecisionsResp)
async def list_decisions() -> DecisionsResp:
    try:
        icgl = get_icgl()
        decisions = getattr(icgl.kb, "human_decisions", {}) if hasattr(icgl, "kb") else {}
        return DecisionsResp(decisions=list(decisions.values()))
    except Exception as e:
        logger.error(f"list_decisions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline", response_model=TimelineResp)
async def governance_timeline() -> TimelineResp:
    try:
        icgl = get_icgl()
        timeline = getattr(icgl.kb, "learning_log", []) if hasattr(icgl, "kb") else []
        return TimelineResp(timeline=timeline)
    except Exception as e:
        logger.error(f"governance_timeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adr/latest", response_model=LatestAdrResp)
async def latest_adr() -> LatestAdrResp:
    try:
        icgl = get_icgl()
        adrs = list(icgl.kb.adrs.values()) if hasattr(icgl, "kb") else []
        if not adrs:
            return LatestAdrResp(adr=None)
        last = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]
        return LatestAdrResp(adr=last.__dict__ if not isinstance(last, dict) else last)
    except Exception as e:
        logger.error(f"latest_adr error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conflicts", response_model=ConflictsResp)
async def list_conflicts() -> ConflictsResp:
    try:
        icgl = get_icgl()
        conflicts = getattr(icgl.kb, "conflicts", []) if hasattr(icgl, "kb") else []
        return ConflictsResp(conflicts=conflicts)
    except Exception as e:
        logger.error(f"list_conflicts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decisions/register", response_model=OperationResult)
async def register_decision(payload: Dict[str, Any]) -> OperationResult:
    try:
        icgl = get_icgl()
        # expected payload: {proposal_id, decision, rationale, signed_by}
        if not hasattr(icgl, "hdal"):
            raise HTTPException(status_code=500, detail="HDAL not available")
        # Delegate to HDAL if API exists
        if hasattr(icgl.hdal, "register_decision"):
            res = icgl.hdal.register_decision(payload)
            return OperationResult(status="ok", result=res if isinstance(res, dict) else {"result": res})
        return OperationResult(status="unsupported", result=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"register_decision error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
