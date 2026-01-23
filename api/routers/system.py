from fastapi import APIRouter

from backend.agents.base import AgentRole

router = APIRouter(prefix="/api/system", tags=["System Visibility"])


@router.get("/secretary-logs")
async def get_secretary_logs(limit: int = 50):
    """
    Exposes the Secretary Agent's internal relay log (The Executive Report).
    """
    from api.server import get_icgl

    try:
        icgl = get_icgl()
        # Access Secretary from Registry
        secretary = icgl.registry.get_agent(AgentRole.SECRETARY)
        if not secretary:
            # Fallback: try string key if Enum fails
            secretary = icgl.registry.get_agent("secretary")

        if not secretary:
            return {"logs": [], "status": "Secretary not active"}

        # Access the relay_log attribute directly
        logs = getattr(secretary, "relay_log", [])

        # Sort by timestamp desc and slice
        sorted_logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

        return {
            "logs": [
                {
                    "timestamp": l.timestamp,
                    "event": l.event_type,
                    "summary": l.summary,
                    "priority": l.priority,
                    "stakeholders": l.stakeholders,
                }
                for l in sorted_logs
            ]
        }
    except Exception as e:
        return {"error": str(e), "logs": []}


@router.get("/sentinel-metrics")
async def get_sentinel_metrics():
    """
    Exposes Sentinel's stability metrics and drift stats.
    """
    from api.server import get_icgl

    try:
        icgl = get_icgl()
        sentinel = icgl.sentinel

        if not sentinel:
            return {"status": "Sentinel not active"}

        # Basic metrics from Sentinel state
        # (Assuming Sentinel has some state or we query the KB/Memory)

        return {
            "status": "active",
            "semantic_memory_size": "Unknown (Adapter Specific)",
            "active_policies": len(icgl.kb.policies),
            "recent_alerts": [],  # Placeholder for now, can be expanded
        }
    except Exception as e:
        return {"error": str(e)}
