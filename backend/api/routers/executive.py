from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException

<<<<<<< HEAD:api/routers/executive.py
from modules.governance.signing_queue import signing_queue
from modules.observability import get_ledger
from modules.observability.events import EventType
=======
from shared.python.governance_shared.governance.signing_queue import signing_queue
from shared.python.observability_shared.observability import get_ledger
from shared.python.observability_shared.observability.events import EventType
>>>>>>> 1017ee5d6165b6b836bcf8f4a86dd3b8c5d9a8a4:backend/api/routers/executive.py

router = APIRouter(prefix="/api/executive", tags=["Executive Agent"])


def _log_executive_event(
    event_type: EventType, user_id: str, trace_id: str, payload: dict
):
    try:
        ledger = get_ledger()
        if hasattr(ledger, "log"):
            ledger.log(
                event_type,
                user_id=user_id,
                trace_id=trace_id,
                input_payload=payload,
            )
    except Exception as e:
        print(f"Log failure: {e}")


@router.get("/queue")
async def get_signing_queue():
    """Returns pending actions and recent history."""
    return {
        "queue": signing_queue.get_pending(),
        "history": signing_queue.get_history(limit=5),
        "status": "ok",
    }


@router.post("/sign/{item_id}")
async def sign_off_action(item_id: str, payload: Dict[str, Any] = Body(...)):
    """
    Sovereign Human Sign-off.
    This authorizes the action for execution (in a future step).
    """
    human_id = payload.get("human_id", "owner")
    result = signing_queue.sign_off(item_id, human_id)

    if result:
        _log_executive_event(
            EventType.HUMAN_INTERVENTION,
            user_id=human_id,
            trace_id=item_id,
            payload={"action": "SIGN", "item": result},
        )
        return {"status": "ok", "result": result}

    raise HTTPException(status_code=404, detail="Item not found or already processed")


@router.post("/reject/{item_id}")
async def reject_action(item_id: str, payload: Dict[str, Any] = Body(...)):
    """
    Sovereign Human Rejection.
    Cancels the action.
    """
    human_id = payload.get("human_id", "owner")
    result = signing_queue.reject(item_id, human_id)

    if result:
        _log_executive_event(
            EventType.HUMAN_INTERVENTION,
            user_id=human_id,
            trace_id=item_id,
            payload={"action": "REJECT", "item": result},
        )
        return {"status": "ok", "result": result}

    raise HTTPException(status_code=404, detail="Item not found or already processed")
