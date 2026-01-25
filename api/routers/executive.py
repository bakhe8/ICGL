from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException

from backend.governance.signing_queue import signing_queue
from backend.observability import get_ledger
from backend.observability.events import EventType

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
