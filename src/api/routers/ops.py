import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.api.schemas import (
    EventsResp,
    ObservabilityStatsResp,
    TraceDetailsResp,
    TracesResp,
    TransactionItem,
    TransactionsList,
)
from src.core.observability import get_ledger
from src.core.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/stats", response_model=ObservabilityStatsResp)
async def get_observability_stats() -> ObservabilityStatsResp:
    """Returns general observability statistics from the ledger."""
    try:
        ledger = get_ledger()
        if not ledger:
            return ObservabilityStatsResp(stats={"status": "no-ledger"})
        stats = ledger.get_stats() if hasattr(ledger, "get_stats") else {"status": "unsupported"}
        return ObservabilityStatsResp(stats=stats)
    except Exception as e:
        logger.error(f"get_observability_stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/alerts", response_model=EventsResp)
async def get_pattern_alerts(limit: int = 10) -> EventsResp:
    """Returns recent pattern violations/alerts detected by the engine."""
    try:
        ledger = get_ledger()
        if not ledger:
            return EventsResp(events=[], count=0)
        # Fallback to querying recent events if specific alert storage isn't found
        events = ledger.query_events(limit=limit) if hasattr(ledger, "query_events") else []
        items = [e.__dict__ if hasattr(e, "__dict__") else e for e in events]
        return EventsResp(events=items, count=len(items))
    except Exception as e:
        logger.error(f"get_pattern_alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces", response_model=TracesResp)
async def list_traces(limit: int = 50) -> TracesResp:
    """Lists recent execution traces."""
    try:
        ledger = get_ledger()
        if not ledger:
            return TracesResp(traces=[], count=0)
        traces = ledger.get_recent_traces(limit=limit) if hasattr(ledger, "get_recent_traces") else []
        return TracesResp(traces=traces, count=len(traces))
    except Exception as e:
        logger.error(f"list_traces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trace/{trace_id}/graph", response_model=TraceDetailsResp)
async def get_trace_graph(trace_id: str) -> TraceDetailsResp:
    """Returns event graph for a specific trace."""
    try:
        ledger = get_ledger()
        if not ledger:
            raise HTTPException(status_code=404, detail="Ledger not initialized")
        events = ledger.get_trace(trace_id) if hasattr(ledger, "get_trace") else []
        items = [e.__dict__ if hasattr(e, "__dict__") else e for e in events]
        return TraceDetailsResp(trace_id=trace_id, event_count=len(items), events=items)
    except Exception as e:
        logger.error(f"get_trace_graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
