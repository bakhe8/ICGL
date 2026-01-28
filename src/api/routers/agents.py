from fastapi import APIRouter, HTTPException

from src.api.deps import get_icgl
from src.api.schemas import (
    AgentEntry,
    AgentHistoryResp,
    AgentRoleResp,
    AgentsList,
    AgentStatsResp,
    GapsList,
)
from src.core.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/list")
async def agents_list() -> AgentsList:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        agents = []
        if registry and hasattr(registry, "list_agents"):
            for role in registry.list_agents():
                agent = registry.get_agent(role)
                agents.append(
                    {
                        "id": getattr(agent, "agent_id", str(role)),
                        "role": str(role),
                        "name": getattr(agent, "name", getattr(agent, "agent_id", str(role))),
                        "description": getattr(agent, "description", ""),
                    }
                )
        return AgentsList(total=len(agents), agents=[AgentEntry(**a) for a in agents])
    except Exception as e:
        logger.error(f"agents_list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gaps")
async def agents_gaps() -> GapsList:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        if registry and hasattr(registry, "find_gaps"):
            gaps = registry.find_gaps()
            return GapsList(gaps=gaps)
        return GapsList()
    except Exception as e:
        logger.error(f"agents_gaps error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/role")
async def agent_role(agent_id: str) -> AgentRoleResp:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        if not registry:
            raise HTTPException(status_code=404, detail="Registry not available")
        agent = registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentRoleResp(id=getattr(agent, "agent_id", agent_id), role=getattr(agent, "role", None))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"agent_role error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/history")
async def agent_history(agent_id: str) -> AgentHistoryResp:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        agent = registry.get_agent(agent_id) if registry and hasattr(registry, "get_agent") else None
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if hasattr(agent, "history"):
            return AgentHistoryResp(history=agent.history())
        return AgentHistoryResp()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"agent_history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/stats")
async def agent_stats(agent_id: str) -> AgentStatsResp:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        agent = registry.get_agent(agent_id) if registry and hasattr(registry, "get_agent") else None
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if hasattr(agent, "stats"):
            return AgentStatsResp(stats=agent.stats())
        return AgentStatsResp()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"agent_stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
