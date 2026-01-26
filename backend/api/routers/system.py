from fastapi import APIRouter

from shared.python.agents_shared.agents.base import AgentRole

router = APIRouter(prefix="/api/system", tags=["System Visibility"])


@router.get("/traffic")
async def get_system_traffic():
    """
    Return real-time message bus traffic for CouncilPulse visualization.
    Reflects the actual 'Sovereign Communication Hub' activity.
    """
    from api.server_shared import get_channel_router

    router_inst = get_channel_router()
    if not router_inst:
        return {"traffic": []}

    # Get recent messages from the in-memory rolling buffer
    raw_traffic = router_inst.get_recent_traffic(limit=20)

    ui_traffic = []
    for msg in raw_traffic:
        try:
            if "->" in msg["channel_id"]:
                parts = msg["channel_id"].split("->")
                to_agent = parts[1]
            else:
                to_agent = "broadcast"

            ui_traffic.append(
                {
                    "from": msg["from_agent"],
                    "to": to_agent,
                    "type": "message",
                    "timestamp": msg["timestamp"],
                }
            )
        except Exception:
            continue

    return {"traffic": ui_traffic}


@router.get("/secretary-logs")
async def get_secretary_logs(limit: int = 50):
    """
    Exposes the Secretary Agent's internal relay log (The Executive Report).
    """
    from api.server_shared import get_icgl

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
                    "timestamp": log_entry.timestamp,
                    "event": log_entry.event_type,
                    "summary": log_entry.summary,
                    "priority": log_entry.priority,
                    "stakeholders": log_entry.stakeholders,
                }
                for log_entry in sorted_logs
            ]
        }
    except Exception as e:
        return {"error": str(e), "logs": []}


@router.get("/sentinel-metrics")
async def get_sentinel_metrics():
    """
    Exposes Sentinel's stability metrics and drift stats.
    """
    from api.server_shared import get_icgl

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
    from api.server_shared import get_icgl

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
    from shared.python.agents_shared.agents.capability_checker import CapabilityChecker
    from backend.system.lifecycle import AgentLifecycleController

    checker = CapabilityChecker()
    # Get real lifecycle states
    lc = AgentLifecycleController()
    states = lc.load_states()

    return {
        "total": len(checker.agents),
        "agents": [
            {
                "id": a.id,
                "name": a.id.title(),
                "role": a.role,
                "capabilities": a.capabilities,
                # Overlay real status from lifecycle controller
                "status": states.get(a.id, a.status),
                "description": f"Sovereign agent specializing in {', '.join(a.capabilities[:2])}.",
            }
            for a in checker.agents.values()
        ],
    }


@router.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """
    Returns the real-time status of a specific agent.
    Used by the Kill Switch UI.
    """
    from backend.system.lifecycle import AgentLifecycleController

    try:
        lc = AgentLifecycleController()
        # The frontend might send "Architect" (capitalize), we should handle it
        # but the lifecycle controller uses whatever key it was saved with.
        # Most internal IDs are lowercase.
        res = lc.get_agent_status(agent_id)
        if hasattr(res, "get"):
            return {"status": res.get("status", "active"), "details": res}
        return {"status": str(res)}
    except Exception as e:
        import logging

        logging.getLogger("api").error(f"Status check failed for {agent_id}: {e}")
        return {"status": "active", "error": str(e)}


@router.get("/agents/gaps")
async def get_agents_gaps():
    """Returns identified capability gaps in the ecosystem."""
    from shared.python.agents_shared.agents.capability_checker import CapabilityChecker

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
    from shared.python.agents_shared.agents.visibility import DEFAULT_ENGINE

    status = DEFAULT_ENGINE.calculate_visibility_status((x, y))
    return {
        "is_visible": status.is_visible,
        "distance": round(status.distance_to_nearest_obstacle, 2),
        "blocked_by": status.blocked_by,
    }
