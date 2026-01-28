from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from src.api.deps import get_icgl
from src.api.schemas import GenericDataResp, OperationResult
from src.api.state import active_synthesis
from src.core.kb.schemas import ADR, uid
from src.core.utils.logging_config import get_logger

from ..background import run_analysis_task

router = APIRouter()
logger = get_logger(__name__)


class ProposalRequest(BaseModel):
    title: str
    context: str
    decision: str
    human_id: str = "bakheet"


class SignRequest(BaseModel):
    action: str
    rationale: str
    human_id: str = "bakheet"


@router.post("/propose", response_model=OperationResult)
async def propose_decision(
    req: ProposalRequest, background_tasks: BackgroundTasks, manager: Any, scp_manager: Any
) -> OperationResult:
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
        active_synthesis[adr.id] = {"status": "processing"}

        background_tasks.add_task(run_analysis_task, adr, req.human_id, active_synthesis, manager, scp_manager)
        return OperationResult(status="Analysis Triggered", result={"adr_id": adr.id})
    except Exception as e:
        logger.error(f"Proposal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=GenericDataResp)
async def get_latest_analysis() -> GenericDataResp:
    icgl = get_icgl()
    adrs = list(icgl.kb.adrs.values())
    if not adrs:
        return GenericDataResp(data={"error": "No ADRs found"})

    last_adr = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]

    if last_adr.id in active_synthesis:
        return GenericDataResp(data=active_synthesis[last_adr.id])

    return GenericDataResp(data={"adr": last_adr.__dict__, "status": "no_active_analysis"})


@router.get("/summary/{adr_id}", response_model=GenericDataResp)
async def get_idea_summary(adr_id: str) -> GenericDataResp:
    icgl = get_icgl()
    adr = icgl.kb.get_adr(adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")

    return GenericDataResp(
        data={
            "id": adr.id,
            "title": adr.title,
            "status": adr.status,
            "context": adr.context[:200] + "..." if len(adr.context) > 200 else adr.context,
            "created_at": adr.created_at,
        }
    )


@router.get("/{adr_id}", response_model=GenericDataResp)
async def get_analysis(adr_id: str) -> GenericDataResp:
    if adr_id in active_synthesis:
        return GenericDataResp(data=active_synthesis[adr_id])
    raise HTTPException(status_code=404, detail="Analysis session context lost or not started.")


@router.post("/sign/{adr_id}", response_model=OperationResult)
async def sign_decision(adr_id: str, req: SignRequest) -> OperationResult:
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(adr_id)
        if not adr:
            raise HTTPException(status_code=404, detail="ADR not found")

        result_data = active_synthesis.get(adr_id)
        if not result_data or "synthesis" not in result_data:
            raise HTTPException(status_code=400, detail="Synthesis data missing.")

        pol = result_data["synthesis"].get("policy_report")
        if pol and pol.get("status") == "FAIL":
            raise HTTPException(status_code=400, detail="Policy gate failed; cannot sign.")
        alerts = result_data["synthesis"].get("sentinel_alerts") or []
        if any(a.get("severity") == "CRITICAL" for a in alerts):
            raise HTTPException(status_code=400, detail="Critical sentinel alert; cannot sign.")

        decision = icgl.hdal.sign_decision(adr_id, req.action, req.rationale, req.human_id)

        adr.status = "ACCEPTED" if req.action == "APPROVE" else "REJECTED"
        adr.human_decision_id = decision.id
        icgl.kb.add_adr(adr)
        icgl.kb.add_human_decision(decision)

        if req.action == "APPROVE" and getattr(icgl, "engineer", None):
            all_changes = []
            for res in result_data["synthesis"]["agent_results"]:
                if "file_changes" in res and res["file_changes"]:
                    from src.core.kb.schemas import FileChange

                    all_changes.extend([FileChange(**fc) for fc in res["file_changes"]])

            if all_changes:
                for change in all_changes:
                    icgl.engineer.write_file(change.path, change.content)
                icgl.engineer.commit_decision(adr, decision)

        return OperationResult(status="Complete", result={"action": req.action})
    except Exception as e:
        logger.error(f"Sign Failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
