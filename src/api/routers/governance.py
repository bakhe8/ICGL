from dataclasses import asdict
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from src.api.deps import get_icgl
from src.api.schemas import (
    ADRSummary,
    ConflictsResp,
    DecisionsResp,
    GenericDataResp,
    LatestAdrResp,
    OperationResult,
    ProposalResp,
    ProposalsList,
    TimelineResp,
)
from src.core.kb.schemas import ADR, uid
from src.core.utils.logging_config import get_logger

from ..background import run_analysis_task

router = APIRouter()
logger = get_logger(__name__)


# --- Schemas ---


class ProposalRequest(BaseModel):
    title: str
    context: str
    decision: str
    human_id: str = "bakheet"


class SignRequest(BaseModel):
    action: str
    rationale: str
    human_id: str = "bakheet"


# --- Active Lifecycle ---


@router.post("/proposals/create", response_model=OperationResult)
@router.post("/propose", response_model=OperationResult)  # Backward compatibility
async def propose_decision(
    req: ProposalRequest, background_tasks: BackgroundTasks, manager: Any = None, scp_manager: Any = None
) -> OperationResult:
    """Creates a new ADR proposal and triggers analysis."""
    logger.info(f"📝 Proposal Received: {req.title}")
    try:
        icgl = get_icgl()
        adr = ADR(
            id=uid(),
            title=req.title,
            status="DRAFT",
            context=req.context,
            decision=req.decision,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )

        icgl.kb.add_adr(adr)
        icgl.kb.save_synthesis_state(adr.id, {"status": "processing"})

        background_tasks.add_task(run_analysis_task, adr, req.human_id, icgl, manager, scp_manager)
        return OperationResult(status="Analysis Triggered", result={"adr_id": adr.id})
    except Exception as e:
        logger.error(f"Proposal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sign/{adr_id}", response_model=OperationResult)
async def sign_decision(adr_id: str, req: SignRequest) -> OperationResult:
    """Signs a decision for an analyzed ADR."""
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(adr_id)
        if not adr:
            raise HTTPException(status_code=404, detail="ADR not found")

        result_data = icgl.kb.get_synthesis_state(adr_id)
        if not result_data or "synthesis" not in result_data:
            # Check if it was already signed or if we can process it directly
            logger.warning(f"Synthesis data missing for {adr_id}. Attempting direct sign.")

        # Policy & Sentinel checks (already done in run_governance_cycle,
        # but here we are in a manual sign-off flow)
        if result_data:
            pol = result_data["synthesis"].get("policy_report")
            if pol and pol.get("status") == "FAIL":
                raise HTTPException(status_code=400, detail="Policy gate failed; cannot sign.")

            alerts = result_data["synthesis"].get("sentinel_alerts") or []
            if any(a.get("severity") == "CRITICAL" for a in alerts):
                raise HTTPException(status_code=400, detail="Critical sentinel alert; cannot sign.")

        decision = icgl.hdal.review_and_sign(
            adr,
            result_data["synthesis"] if result_data else None,
            req.human_id,
            action=req.action,
            rationale=req.rationale,
        )

        if decision:
            # Persist and execute (icgl.py logic is mirrored here for API responsiveness)
            # Standardizing: The API should ideally just call engine.finalize_cycle(adr, decision)
            # For now, we update status and save.
            adr.status = "ACCEPTED" if req.action == "APPROVE" else "REJECTED"
            adr.human_decision_id = decision.id
            icgl.kb.add_adr(adr)
            icgl.kb.add_human_decision(decision)

            # Record in Merkle Ledger
            icgl.observer.record_decision(
                {
                    "adr_id": adr.id,
                    "decision_id": decision.id,
                    "action": decision.action,
                    "rationale": decision.rationale,
                    "signed_by": decision.signed_by,
                    "timestamp": decision.timestamp,
                    "signature_hash": decision.signature_hash,
                }
            )

            if req.action == "APPROVE" and getattr(icgl, "engineer", None) and result_data:
                # Engineer logic (optional)
                pass

        return OperationResult(status="Complete", result={"action": req.action})
    except Exception as e:
        logger.error(f"Sign Failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --- Historical & Query ---


@router.get("/proposals", response_model=ProposalsList)
async def list_proposals(state: Optional[str] = None) -> ProposalsList:
    """Lists all ADR proposals, optionally filtered by state."""
    try:
        icgl = get_icgl()
        adrs = list(icgl.kb.adrs.values())
        if state:
            adrs = [a for a in adrs if getattr(a, "status", "") == state.upper()]

        items = [
            ADRSummary(
                id=str(a.id),
                title=str(a.title),
                status=str(a.status),
                created_at=str(a.created_at),
            )
            for a in adrs
        ]
        return ProposalsList(proposals=items)
    except Exception as e:
        logger.error(f"list_proposals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}", response_model=ProposalResp)
async def get_proposal(proposal_id: str) -> ProposalResp:
    """Returns detailed information for a specific proposal."""
    icgl = get_icgl()
    adr = icgl.kb.get_adr(proposal_id)
    if not adr:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return ProposalResp(proposal=asdict(adr))


@router.get("/decisions", response_model=DecisionsResp)
async def list_decisions() -> DecisionsResp:
    """Lists all signed human decisions."""
    icgl = get_icgl()
    decisions = icgl.kb.human_decisions
    items = []
    for d in decisions.values():
        item = asdict(d)
        if "action" in item and hasattr(item["action"], "value"):
            item["action"] = item["action"].value
        items.append(item)
    return DecisionsResp(decisions=items)


@router.get("/timeline", response_model=TimelineResp)
async def governance_timeline() -> TimelineResp:
    """Returns the ICGL learning log as a timeline."""
    icgl = get_icgl()
    logs = icgl.kb.learning_log
    items = []
    from src.core.kb.schemas import now

    for log in logs:
        data = asdict(log)
        items.append(
            {
                "id": f"cycle-{data.get('cycle', 0)}",
                "timestamp": data.get("timestamp") or now(),
                "type": "CYCLE_UPDATE",
                "label": data.get("summary") or f"Cycle {data.get('cycle')} Completed",
                "source": "ICGL Engine",
                "severity": "info",
                "payload": data,
            }
        )
    items.sort(key=lambda x: x.get("payload", {}).get("cycle", 0), reverse=True)
    return TimelineResp(timeline=items)


@router.get("/adr/latest", response_model=LatestAdrResp)
@router.get("/latest", response_model=LatestAdrResp)
async def latest_adr() -> LatestAdrResp:
    """Returns the most recently created ADR."""
    icgl = get_icgl()
    adrs = list(icgl.kb.adrs.values())
    if not adrs:
        return LatestAdrResp(adr=None)
    last = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]

    # Check if active synthesis exists in KB
    state = icgl.kb.get_synthesis_state(last.id)
    if state:
        # For now, just return ADR. UI query handles mixing.
        pass

    item = asdict(last)
    if "status" in item and hasattr(item["status"], "value"):
        item["status"] = item["status"].value
    return LatestAdrResp(adr=item)


@router.get("/conflicts", response_model=ConflictsResp)
async def list_conflicts() -> ConflictsResp:
    """Lists detected policy or sentinel conflicts."""
    icgl = get_icgl()
    conflicts = getattr(icgl.kb, "conflicts", [])
    return ConflictsResp(conflicts=conflicts)


@router.get("/analysis/{adr_id}", response_model=GenericDataResp)
@router.get("/{adr_id}", response_model=GenericDataResp)  # Compatibility
async def get_analysis(adr_id: str) -> GenericDataResp:
    """Returns the active analysis/synthesis result for an ADR."""
    icgl = get_icgl()
    state = icgl.kb.get_synthesis_state(adr_id)
    if state:
        return GenericDataResp(data=state)

    # Fallback: check if we have a persisted ADR but no active synthesis
    adr = icgl.kb.get_adr(adr_id)
    if adr:
        return GenericDataResp(data={"adr": asdict(adr), "status": "completed"})

    raise HTTPException(status_code=404, detail="Analysis session not found.")
