import os
import time
import shutil
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.dependencies import _require_api_key, root_dir

router = APIRouter(prefix="/api/system", tags=["System"])

# Tracking app start time (moved logic from main/dependencies)
from api.dependencies import logger, get_agent_registry, get_consensus_service
from agents.registry import AgentRegistry
from agents.base import Problem

@router.get("/agents")
async def list_agents_registry():
    """Returns the list of active agents and their metadata."""
    registry = get_agent_registry()
    roles = registry.list_agents()
    
    # Metadata mapping based on fallback data
    metadata = {
        "architect": {
            "department": "الهندسة",
            "description": "Architectural integrity and system design.",
            "capabilities": ["Design review", "System topology", "Integrity checks"]
        },
        "policy": {
            "department": "الحوكمة",
            "description": "Policy Editor · Rules Engine",
            "capabilities": ["Policy edit", "Rules validation", "Escalation to HDAL"]
        },
        "sentinel": {
            "department": "الأمن",
            "description": "Drift Monitor · Pattern Alerts",
            "capabilities": ["Risk scans", "Drift detection", "Pattern alerts"]
        },
        "engineer": {
            "department": "العمليات",
            "description": "GitOps / Version Control and machinery.",
            "capabilities": ["GitOps posture", "Branch hygiene", "Deploy gates"]
        },
        "builder": {
            "department": "العمليات",
            "description": "Code generation and implementation.",
            "capabilities": ["Scaffold code", "Draft PR plans", "Refactoring"]
        },
        "monitor": {
            "department": "الأمن",
            "description": "Real-time system monitoring.",
            "capabilities": ["Log analysis", "Health checks"]
        },
        "archivist": {
            "department": "الأرشيف",
            "description": "Documents Workspace · ADR Steward",
            "capabilities": ["Document drafts", "Gap analysis", "ADR lifecycle"]
        },
        "secretary": {
            "department": "المكتب التنفيذي",
            "description": "Open Door · Translation · Relay Log",
            "capabilities": ["Relay log", "Translate requests", "Executive intake"]
        },
        "hr": {
            "department": "الموارد البشرية",
            "description": "Responsibility Matrix · Role Definitions",
            "capabilities": ["Role updates", "Org chart", "Responsibility docs"]
        }
    }

    agents_list = []
    for role in roles:
        agent = registry.get_agent(role)
        if agent:
            role_val = agent.role.value
            meta = metadata.get(role_val, {
                "department": "General",
                "description": f"Specialized {role_val} agent.",
                "capabilities": []
            })
            agents_list.append({
                "id": agent.agent_id.replace("agent-", ""),
                "name": agent.agent_id.split("-")[-1].capitalize(),
                "role": role_val,
                "status": "active",
                "signals": ["Live"],
                "department": meta["department"],
                "description": meta["description"],
                "capabilities": meta["capabilities"],
                "fidelity": "live"
            })
    return {"agents": agents_list}

class AgentRunRequest(BaseModel):
    title: str
    context: str

@router.post("/agents/{agent_id}/run")
async def run_specific_agent(
    agent_id: str,
    request: AgentRunRequest,
    registry: AgentRegistry = Depends(get_agent_registry)
):
    """
    Run a specific agent for ad-hoc analysis.
    """
    agent = registry.get_agent_by_role(agent_id) or registry.get_agent_by_role(agent_id.lower())
    if not agent:
        # Fallback search by ID if role doesn't match
        found = next((a for a in registry.agents.values() if a.agent_id.lower() == agent_id.lower()), None)
        if found:
            agent = found
        else:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    try:
        # Get KnowledgeBase for agent context
        service = get_consensus_service()
        # ConsensusService acts as the provider; we pass it directly or None.
        # It does NOT have a .kb attribute.
        kb = service 

        # Construct a proper Problem object
        # Some agents (like Engineer) ignore it, but others need the structure.
        problem = Problem(
            title=request.title,
            context=request.context,
            related_files=[],
            metadata={"source": "manual_run"}
        )
        
        result = await agent.analyze(problem, kb=kb)
        
        return {
            "agent": agent.agent_id,
            "role": agent.role.value,
            "confidence": result.confidence,
            "analysis": result.analysis,
            "recommendations": result.recommendations,
            "concerns": result.concerns,
            "references": result.references
        }
    except Exception as e:
        logger.error(f"Agent Run Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Diagnostic endpoint to verify system sanity."""
    status = {
        "api": "healthy",
        "env_loaded": "OPENAI_API_KEY" in os.environ,
        "db_lock": "none",
        "engine_ready": False
    }
    
    try:
        from api.dependencies import get_consensus_service
        service = get_consensus_service()
        status["engine_ready"] = service is not None
        status["db_lock"] = "none"
        
        # Access start_time_app - we'll need to pass this or import from main
        # For now, we'll try to get it from a global or mock
        try:
            from api.main import start_time_app
        except ImportError:
            start_time_app = time.time()

        # Extended Health Info
        try:
            import psutil
            process = psutil.Process(os.getpid())
            status["system"] = {
                "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
                "cpu_percent": psutil.cpu_percent(),
                "uptime_seconds": round(time.time() - start_time_app, 2),
                "thread_count": process.num_threads()
            }
        except ImportError:
            status["system"] = {
                "uptime_seconds": round(time.time() - start_time_app, 2),
                "info": "psutil not installed for detailed telemetry"
            }
    except Exception as e:
        status["api"] = "degraded"
        status["db_error"] = str(e)
        
    return status

@router.get("/status")
async def get_status():
    """Returns general system status and metrics for the dashboard."""
    try:
        from api.dependencies import get_consensus_service
        service = get_consensus_service()
        
        total, used, free = shutil.disk_usage("/")
        adrs = service.adr_repo.get_all()
        
        return {
            "kb_stats": {
                "adrs": len(adrs),
                "policies": len(service.policy_repo.get_all()),
                "last_update": time.time()
            },
            "system_load": {
                "disk_free_gb": free // (2**30),
                "api_latency_ms": 12 # Mock
            },
            "sovereign_status": "Active"
        }
    except Exception as e:
        logger.error(f"Status Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/dashboard/quick")
async def get_dashboard_quick():
    """Minimal telemetry for sidebar indicators."""
    try:
        from api.dependencies import get_consensus_service
        service = get_consensus_service()
        adrs = service.adr_repo.get_all()
        pending = [a for a in adrs if (a.get("status") or "").upper() == "PROPOSED"]
        return {
            "active_trials": 0,
            "pending_adrs": len(pending),
            "integrity_score": 100 if len(adrs) > 0 else 98
        }
    except Exception:
        return {
            "active_trials": 0,
            "pending_adrs": 0,
            "integrity_score": 90
        }

@router.get("/docs/tree")
async def get_docs_tree():
    """Recursively build the docs tree from data/ai_workspace + KB policy files."""
    base_path = root_dir / "data" / "ai_workspace"
    kb_path = root_dir / "data"
    if not base_path.exists():
        # Fallback to current directory for demo if data/ai_workspace doesn't exist?
        # No, better to stick to the intended structure.
        base_path.mkdir(parents=True, exist_ok=True)

    def build_tree(path):
        roots = []
        try:
            # Sort directories first, then files
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items:
                node = {
                    "name": item.name,
                    "path": str(item.relative_to(base_path)).replace("\\", "/"),
                    "type": "folder" if item.is_dir() else "file"
                }
                if item.is_dir():
                    node["children"] = build_tree(item)
                roots.append(node)
        except PermissionError:
            pass
        return roots

    roots = build_tree(base_path)

    # Attach KB policy files as a dedicated node
    policy_children = []
    for fname in ["kb_policies.json", "kb_policies_drafts.json"]:
        fpath = kb_path / fname
        if fpath.exists():
            policy_children.append({
                "name": fname,
                "path": f"kb/{fname}",
                "type": "file"
            })
    if policy_children:
        roots.append({
            "name": "kb_policies",
            "path": "kb",
            "type": "folder",
            "children": policy_children
        })

    return {"roots": roots}

def _resolve_doc_path(path: str):
    """Resolve a doc path against allowed roots (ai_workspace + data/kb*)."""
    workspace_base = (root_dir / "data" / "ai_workspace").resolve()
    kb_base = (root_dir / "data").resolve()

    target = (workspace_base / path).resolve()
    if str(target).startswith(str(workspace_base)):
        return target

    kb_target = (kb_base / path.replace("kb/", "", 1)).resolve() if path.startswith("kb/") else None
    if kb_target and str(kb_target).startswith(str(kb_base)):
        return kb_target
    return None

@router.get("/docs/content")
async def get_doc_content(path: str):
    """Safe file read from data/ai_workspace or KB policy files."""
    target = _resolve_doc_path(path)
    if not target:
        return JSONResponse(status_code=403, content={"error": "Access denied"})
    if not target.exists() or not target.is_file():
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        return {"path": path, "content": content, "mime": "text/plain"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/docs/save")
async def save_doc(request: Request):
    """Save content to an allowed doc path (workspace or KB policy files)."""
    try:
        data = await request.json()
        path = data.get("path")
        content = data.get("content", "")
        target = _resolve_doc_path(path or "")
        if not target:
            return JSONResponse(status_code=403, content={"error": "Access denied"})
        
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"status": "saved", "path": path}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
