import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.api.schemas import TransactionItem, TransactionsList
from src.core.observability import get_ledger
from src.core.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/transactions", response_model=TransactionsList)
async def list_transactions(limit: int = 100) -> TransactionsList:
    try:
        ledger = get_ledger()
        if not ledger:
            return TransactionsList(transactions=[], count=0)
        # Try common method names used by ledger implementations
        if hasattr(ledger, "get_transactions"):
            txs = ledger.get_transactions(limit=limit)
        elif hasattr(ledger, "list_transactions"):
            txs = ledger.list_transactions(limit=limit)
        else:
            # Fallback to recent traces/events as a proxy
            txs = getattr(ledger, "get_recent_traces", lambda limit=limit: [])(limit)
        items = []
        for t in txs:
            if isinstance(t, dict):
                items.append(TransactionItem(id=t.get("id"), type=t.get("type"), detail=t))
            else:
                items.append(
                    TransactionItem(
                        id=getattr(t, "id", None), type=getattr(t, "type", None), detail=getattr(t, "__dict__", {})
                    )
                )
        return TransactionsList(transactions=items, count=len(items))
    except Exception as e:
        logger.error(f"list_transactions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pulse/stream", include_in_schema=False)
async def pulse_stream(interval: float = 2.0):
    """Server-Sent Events stream that emits lightweight pulse messages."""

    async def event_generator():
        try:
            while True:
                ledger = get_ledger()
                stats = ledger.get_stats() if ledger and hasattr(ledger, "get_stats") else {"status": "no-ledger"}
                payload = {"type": "pulse", "stats": stats}
                yield f"data: {json.dumps(payload, default=str)}\n\n"
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            return

    return StreamingResponse(event_generator(), media_type="text/event-stream")
