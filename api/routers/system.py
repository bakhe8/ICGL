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


@router.get("/metrics")
async def get_system_metrics():
    """
    Returns high-level system metrics (Soul Vitals).
    Maps to /api/system/metrics
    """

    # Mock/Heuristic data for now until we have real telemetry
    return {
        "chaosLevel": 0.05,  # Low chaos (5%)
        "efficiency": 0.92,  # High efficiency (92%)
        "databaseIntegrity": 1.0,  # Perfect integrity
    }


@router.get("/committee")
async def get_committee_members():
    """
    Returns list of active Sovereign Committee members.
    Maps to /api/system/committee
    """
    from api.server import get_icgl

    try:
        icgl = get_icgl()
        agents = []
        if icgl.registry and icgl.registry._agents:
            for role, agent in icgl.registry._agents.items():
                agents.append(
                    {
                        "name": agent.agent_id,
                        "role": role.value,
                        "specialty": getattr(agent, "specialty", "Sovereign Agent"),
                    }
                )
        return agents
    except Exception:
        return []


@router.get("/agents/list")
async def get_agents_list():
    """Returns the full agent registry with capabilities from CapabilityChecker."""
    from backend.agents.capability_checker import CapabilityChecker

    checker = CapabilityChecker()
    return {
        "total": len(checker.agents),
        "agents": [
            {
                "id": a.id,
                "name": a.id.title(),
                "role": a.role,
                "capabilities": a.capabilities,
                "status": a.status,
                "description": f"Sovereign agent specializing in {', '.join(a.capabilities[:2])}.",
            }
            for a in checker.agents.values()
        ],
    }


@router.get("/agents/gaps")
async def get_agents_gaps():
    """Returns identified capability gaps in the ecosystem."""
    from backend.agents.capability_checker import CapabilityChecker

    checker = CapabilityChecker()
    gaps = checker.list_gaps()

    # Categorize gaps
    critical = [
        {"name": name, "priority": priority}
        for name, priority in gaps.items()
        if priority == "ACTIVE"
    ]
    medium = [
        {"name": name, "priority": priority}
        for name, priority in gaps.items()
        if priority == "MEDIUM"
    ]
    enhancement = [
        {"name": name, "priority": priority}
        for name, priority in gaps.items()
        if priority == "ENHANCEMENT"
    ]

    return {
        "total_gaps": len(gaps),
        "critical": critical,
        "medium": medium,
        "enhancement": enhancement,
    }


@router.get("/agents/visibility")
async def get_agents_visibility(x: float = 0.0, y: float = 0.0):
    """Calculates agent visibility at a specific coordinate."""
    from backend.agents.visibility import DEFAULT_ENGINE

    status = DEFAULT_ENGINE.calculate_visibility_status((x, y))
    return {
        "is_visible": status.is_visible,
        "distance": round(status.distance_to_nearest_obstacle, 2),
        "blocked_by": status.blocked_by,
    }
