from typing import Dict

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ADRSummary, ExecutiveQueue, OperationResult
from backend.api.server import get_icgl
from shared.python.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/queue", response_model=ExecutiveQueue)
async def executive_queue() -> ExecutiveQueue:
    try:
        icgl = get_icgl()
        # The executive queue is represented by DRAFT ADRs waiting for human action
        adrs = list(icgl.kb.adrs.values()) if hasattr(icgl, "kb") else []
        queue = [a for a in adrs if getattr(a, "status", "") in ("DRAFT", "READY")]
        items = [
            ADRSummary(
                id=getattr(a, "id", None),
                title=getattr(a, "title", None),
                status=getattr(a, "status", None),
                created_at=str(getattr(a, "created_at", None)),
            )
            for a in queue
        ]
        return ExecutiveQueue(queue=items)
    except Exception as e:
        logger.error(f"executive_queue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sign/{adr_id}", response_model=OperationResult)
async def executive_sign(adr_id: str, payload: Dict[str, str]) -> OperationResult:
    try:
        icgl = get_icgl()
        # Reuse existing sign flow if available
        from backend.api.server import sign_decision as global_sign

        # payload expected: {action, rationale, human_id}
        try:
            return await global_sign(adr_id, type("P", (), payload))
        except Exception:
            # fallback: call hdal directly
            if hasattr(icgl, "hdal") and hasattr(icgl.hdal, "sign_decision"):
                res = icgl.hdal.sign_decision(
                    adr_id, payload.get("action"), payload.get("rationale"), payload.get("human_id", "operator")
                )
                return OperationResult(status="ok", result=res if isinstance(res, dict) else {"result": res})
        return {"status": "unsupported"}
    except Exception as e:
        logger.error(f"executive_sign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject/{adr_id}", response_model=OperationResult)
async def executive_reject(adr_id: str, payload: Dict[str, str]) -> OperationResult:
    try:
        # Signing with REJECT action
        payload = payload or {}
        payload["action"] = payload.get("action", "REJECT")
        return await executive_sign(adr_id, payload)
    except Exception as e:
        logger.error(f"executive_reject error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
