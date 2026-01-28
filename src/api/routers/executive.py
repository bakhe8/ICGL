from typing import Dict

from fastapi import APIRouter, HTTPException

from src.api.deps import get_icgl
from src.api.schemas import ADRSummary, ExecutiveQueue, OperationResult
from src.core.utils.logging_config import get_logger

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
                id=str(getattr(a, "id", "")),
                title=str(getattr(a, "title", "No Title")),
                status=str(getattr(a, "status", "DRAFT")),
                created_at=str(getattr(a, "created_at", "")),
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
        # payload expected: {action, rationale, human_id}

        from src.api.server import SignRequest
        from src.api.server import sign_decision as global_sign

        sign_req = SignRequest(
            action=payload.get("action", "APPROVE"),
            rationale=payload.get("rationale", ""),
            human_id=payload.get("human_id", "operator"),
        )

        try:
            return await global_sign(adr_id, sign_req)
        except Exception:
            # fallback: call hdal directly
            if hasattr(icgl, "hdal") and hasattr(icgl.hdal, "sign_decision"):
                res = icgl.hdal.sign_decision(
                    adr_id, payload.get("action"), payload.get("rationale"), payload.get("human_id", "operator")
                )
                return OperationResult(status="ok", result=res if isinstance(res, dict) else {"result": res})
        return OperationResult(status="unsupported")
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
