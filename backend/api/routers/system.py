from typing import Dict

from fastapi import APIRouter, HTTPException

from backend.api.deps import get_icgl
from backend.api.schemas import (
    AgentEntry,
    AgentsList,
    DocsContentResp,
    DocsSaveResp,
    DocsTreeResp,
    OperationResult,
    SecretaryLogsResp,
    SentinelMetricsResp,
    StatusResp,
    TrafficResp,
)
from shared.python.observability import get_ledger
from shared.python.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/agents", response_model=AgentsList)
async def list_agents() -> AgentsList:
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
        logger.error(f"list_agents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/run", response_model=OperationResult)
async def run_agent(agent_id: str, payload: dict) -> OperationResult:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        if not registry:
            raise HTTPException(status_code=404, detail="Registry not available")
        # Attempt to run a single agent via registry API if available
        if hasattr(registry, "run_single_agent"):
            res = await registry.run_single_agent(agent_id, payload, icgl.kb)
            return OperationResult(status="ok", result=res if isinstance(res, dict) else {"result": res})
        return OperationResult(status="unsupported", result=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"run_agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/status", response_model=StatusResp)
async def agent_status(agent_id: str) -> StatusResp:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        if registry and hasattr(registry, "get_agent"):
            agent = registry.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
            return StatusResp(status=getattr(agent, "status", "idle"))
        return StatusResp(status="unknown")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"agent_status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/lifecycle", response_model=OperationResult)
async def agent_lifecycle(agent_id: str, payload: dict) -> OperationResult:
    try:
        icgl = get_icgl()
        registry = getattr(icgl, "registry", None)
        if registry and hasattr(registry, "get_agent"):
            agent = registry.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
            # allow agent to handle lifecycle if method exists
            if hasattr(agent, "lifecycle_action"):
                res = agent.lifecycle_action(payload)
                return OperationResult(status="ok", result=res if isinstance(res, dict) else {"result": res})
        return OperationResult(status="unsupported", result=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"agent_lifecycle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/secretary-logs", response_model=SecretaryLogsResp)
async def secretary_logs(limit: int = 5) -> SecretaryLogsResp:
    try:
        icgl = get_icgl()
        hdal = getattr(icgl, "hdal", None)
        logs = []
        if hdal and hasattr(hdal, "observer") and hasattr(hdal.observer, "recent_logs"):
            logs = hdal.observer.recent_logs(limit=limit)
        return SecretaryLogsResp(logs=logs, status="ok")
    except Exception as e:
        logger.error(f"secretary_logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentinel-metrics", response_model=SentinelMetricsResp)
async def sentinel_metrics() -> SentinelMetricsResp:
    try:
        icgl = get_icgl()
        sentinel = getattr(icgl, "sentinel", None)
        if sentinel and hasattr(sentinel, "metrics"):
            return SentinelMetricsResp(metrics=sentinel.metrics())
        return SentinelMetricsResp(metrics={})
    except Exception as e:
        logger.error(f"sentinel_metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traffic", response_model=TrafficResp)
async def system_traffic() -> TrafficResp:
    try:
        # Simple traffic summary from observability ledger if available
        ledger = get_ledger()
        if ledger and hasattr(ledger, "get_traffic"):
            return TrafficResp(traffic=ledger.get_traffic())
        return TrafficResp(traffic=[])
    except Exception as e:
        logger.error(f"system_traffic error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/docs/tree", response_model=DocsTreeResp)
async def docs_tree() -> DocsTreeResp:
    try:
        icgl = get_icgl()
        kb = getattr(icgl, "kb", None)
        if kb and hasattr(kb, "list_docs"):
            return DocsTreeResp(roots=kb.list_docs())
        # Fallback: read docs from data/kb if present
        from pathlib import Path

        base = Path("data/kb")
        roots = []
        if base.exists():
            for p in base.iterdir():
                roots.append({"name": p.name, "path": str(p)})
        return DocsTreeResp(roots=roots)
    except Exception as e:
        logger.error(f"docs_tree error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/docs/content", response_model=DocsContentResp)
async def docs_content(path: str) -> DocsContentResp:
    try:
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            # try relative to data/kb
            p = Path("data/kb") / path
        if not p.exists():
            raise HTTPException(status_code=404, detail="Doc not found")
        content = p.read_text(encoding="utf-8")
        mime = "text/plain"
        return DocsContentResp(path=str(p), content=content, mime=mime)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"docs_content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/docs/save", response_model=DocsSaveResp)
async def docs_save(payload: Dict[str, str]) -> DocsSaveResp:
    try:
        path = payload.get("path")
        content = payload.get("content")
        if not path or content is None:
            raise HTTPException(status_code=400, detail="Missing path or content")
        from pathlib import Path

        p = Path(path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return DocsSaveResp(status="ok", path=str(p))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"docs_save error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
