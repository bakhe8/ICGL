import time

import psutil
from fastapi import APIRouter, Query

from backend.observability import get_detector, get_ledger

router = APIRouter(prefix="/api/observability", tags=["observability"])


@router.get("/alerts")
async def get_pattern_alerts(limit: int = Query(10, ge=1)):
    """
    Returns detected pattern alerts from the PatternDetector.
    CHECKLIST: Align with /patterns/alerts requirement.
    """
    detector = get_detector()
    # In a real scenario, we'd fetch these from the ledger or a live buffer.
    # For now, we fetch the most recent ones detected.
    alerts = detector.get_active_alerts()[:limit]
    return {"alerts": alerts}


@router.get("/stats")
async def get_observability_stats():
    """Returns system-wide observability metrics."""
    ledger = get_ledger()
    return ledger.get_stats()


@router.get("/events")
async def get_events(limit: int = 50):
    """Returns recent events from the ledger."""
    ledger = get_ledger()
    return ledger.query_events(limit=limit)


@router.get("/metrics")
async def get_live_metrics():
    """
    Phase 7: Real-time Operational Metrics.
    Returns live resource usage and simulated task costs.
    """
    cpu_usage = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()

    # Simulate dynamic task cost based on ledger activity
    ledger = get_ledger()
    recent_events = ledger.query_events(limit=10)
    avg_cost = 0.05 * len(recent_events)  # Simulated metric

    return {
        "cpu": cpu_usage,
        "memory": {
            "percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
        },
        "task_efficiency": {
            "avg_cost_per_task": avg_cost,
            "active_tasks": len(
                [e for e in recent_events if "start" in e.get("type", "").lower()]
            ),
        },
        "timestamp": time.time(),
    }
