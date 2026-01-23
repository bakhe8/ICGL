import asyncio
import json
import os
import threading
import time
import traceback

# ICGL Core Imports
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from dotenv import load_dotenv
from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.quick_code_endpoint import router as quick_router
from backend.agents.base import Problem

# Quick code endpoint
from backend.core.runtime_guard import RuntimeIntegrityGuard
from backend.governance import ICGL
from backend.kb import ADR
from backend.kb.schemas import DecisionAction, HumanDecision, now, uid
from backend.observability import get_ledger
from backend.observability.events import EventType
from backend.utils.logging_config import get_logger

# 1. 🔴 MANDATORY: Load Environment FIRST (Root Cause Fix for OpenAI Key)
# We find the .env relative to this file's root
# Project root (ICGL)
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Path map for UI routes -> source files
PATH_MAP_FILE = BASE_DIR / "config" / "path_map.json"
PATH_MAP_CACHE: Dict[str, str] = {}


def load_path_map() -> Dict[str, str]:
    global PATH_MAP_CACHE
    if PATH_MAP_CACHE:
        return PATH_MAP_CACHE
    if PATH_MAP_FILE.exists():
        try:
            PATH_MAP_CACHE = json.loads(PATH_MAP_FILE.read_text(encoding="utf-8"))
        except Exception:
            PATH_MAP_CACHE = {}
    return PATH_MAP_CACHE


def resolve_targets_from_text(text: str) -> List[str]:
    """Find target files based on path map and URLs mentioned in idea text."""
    path_map = load_path_map()
    targets: List[str] = []
    for token in text.split():
        token = token.strip().strip("\",'")
        if token in path_map:
            targets.append(path_map[token])
        # handle full URL containing path
        for route, dest in path_map.items():
            if route in token and dest not in targets:
                targets.append(dest)
    return targets


def log_idea_event(
    adr_id: str,
    idea: str,
    target_files: List[str],
    applied: List[dict],
    skipped: List[dict],
) -> None:
    """Append idea execution metadata to a JSONL log for traceability."""
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "idea_runs.jsonl"
    record = {
        "adr_id": adr_id,
        "idea": idea,
        "target_files": target_files,
        "applied_changes": applied,
        "skipped_changes": skipped,
        "timestamp": now(),
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_event(
    message: str,
    event_type: str = EventType.SYSTEM_EVENT,
    trace_id: Optional[str] = None,
    payload: Optional[dict] = None,
    user_id: Optional[str] = None,
    agent: Optional[str] = None,
) -> None:
    """
    Lightweight helper to log to the observability ledger and ignore failures.
    Adds agent/user_id when provided so UI can map events to specific agents.
    """
    try:
        ledger = get_ledger()
        if hasattr(ledger, "log"):
            input_payload = {"message": message, **(payload or {})}
            if agent:
                input_payload.setdefault("agent", agent)
            ledger.log(
                EventType(event_type),
                user_id=user_id or agent or "system",
                trace_id=trace_id or "general",
                input_payload=input_payload,
            )
    except Exception as e:
        logger.warning(f"Event log failed: {e}")


# Initialize logger
logger = get_logger(__name__)

if not os.getenv("OPENAI_API_KEY"):
    logger.warning("❌ OPENAI_API_KEY NOT FOUND IN ENVIRONMENT!")

# Initialize FastAPI
app = FastAPI(title="ICGL Sovereign Cockpit API", version="1.2.0")
app.include_router(quick_router)

rebuild_lock = asyncio.Lock()


@app.post("/api/rebuild")
async def rebuild_frontend():
    """
    Trigger frontend rebuild (web/) so new generated files appear.
    """
    import shutil
    import subprocess

    if rebuild_lock.locked():
        return {"status": "busy", "message": "Rebuild already running"}

    async with rebuild_lock:
        try:
            loop = asyncio.get_running_loop()

            def run_build():
                npm_path = shutil.which("npm")
                if not npm_path:
                    npm_path = shutil.which("npm.cmd")
                if not npm_path:
                    return 127, "", "npm not found in PATH"

                # Base dir of project
                base_dir = Path(__file__).parent.parent
                proc = subprocess.run(
                    [npm_path, "run", "build"],
                    cwd=str(base_dir / "web"),
                    capture_output=True,
                    text=True,
                    shell=True,
                )
                return proc.returncode, proc.stdout, proc.stderr

            code, out, err = await loop.run_in_executor(None, run_build)
            status = "ok" if code == 0 else "failed"
            return {
                "status": status,
                "code": code,
                "stdout": (out or "")[-4000:],
                "stderr": (err or "")[-4000:],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


@app.post("/rebuild")  # Compatibility alias
async def rebuild_alias():
    return await rebuild_frontend()


def custom_openapi():
    """
    Generate OpenAPI schema while normalizing empty schemas to valid objects
    to keep Swagger UI from crashing on undefined .slice calls.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title, version=app.version, routes=app.routes
    )
    # Swagger UI is happier with 3.0.x; downgrade version string to avoid UI bugs.
    openapi_schema["openapi"] = "3.0.3"
    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            for response in operation.get("responses", {}).values():
                content = response.get("content", {})
                for media in content.values():
                    schema = media.get("schema")
                    if schema == {} or schema is None:
                        media["schema"] = {"type": "object"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Disable caching for dashboard assets to avoid stale UI
@app.middleware("http")
async def disable_dashboard_cache(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/dashboard"):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# --- Global Engine Singleton ---
# Initialized lazily with thread-safe double-checked locking
_icgl_instance: Optional[ICGL] = None
_icgl_lock = threading.Lock()

# --- Global Channel Router ---
_channel_router = None

# --- In-memory conflicts (placeholder until persistence is added) ---
_conflicts: List[Dict[str, Any]] = []


# --- Request Models ---
class ProposalRequest(BaseModel):
    title: str
    context: str
    decision: str
    human_id: str = "bakheet"


class IdeaRequest(BaseModel):
    """Lightweight idea input; will be transformed into an ADR for execution."""

    idea: str
    human_id: str = "bakheet"


class SignRequest(BaseModel):
    action: str
    rationale: str
    human_id: str = "bakheet"


class AgentRunRequest(BaseModel):
    title: str
    context: str


class DecisionRegisterRequest(BaseModel):
    proposal_id: str
    decision: str
    rationale: str
    signed_by: str = "operator"


class TerminalRequest(BaseModel):
    cmd: str
    path: Optional[str] = None
    lines: Optional[int] = None
    content: Optional[str] = None


class FileWriteRequest(BaseModel):
    path: str
    content: str
    mode: str = "w"


# Rebuild ForwardRefs for OpenAPI generation
AgentRunRequest.model_rebuild()
DecisionRegisterRequest.model_rebuild()
TerminalRequest.model_rebuild()
FileWriteRequest.model_rebuild()


def get_channel_router():
    """Get the global channel router instance"""
    # Force ICGL initialization first (which initializes router)
    get_icgl()
    return _channel_router


def get_icgl() -> ICGL:
    """Get or create the ICGL engine singleton (thread-safe)."""
    global _icgl_instance
    if _icgl_instance is None:
        with _icgl_lock:
            # Double-check after acquiring lock
            if _icgl_instance is None:
                logger.info("🚀 Booting ICGL Engine Singleton...")
                try:
                    # Initialize Observability FIRST (before any agents run)
                    from backend.observability import init_observability

                    obs_db_path = BASE_DIR / "data" / "observability.db"
                    init_observability(str(obs_db_path))
                    logger.info("📊 Observability Ledger Initialized")

                    # Runtime integrity check
                    rig = RuntimeIntegrityGuard()
                    rig.check()

                    # Boot ICGL
                    _icgl_instance = ICGL()
                    logger.info("✅ Engine Booted Successfully.")

                    # Initialize Direct Channel Router AFTER ICGL (Phase 2)
                    from backend.coordination.router import DirectChannelRouter

                    global _channel_router
                    _channel_router = DirectChannelRouter(
                        icgl_provider=lambda: _icgl_instance
                    )
                    logger.info("🔀 Direct Channel Router Initialized")

                except Exception as e:
                    logger.critical(f"❌ Engine Boot Failed: {e}", exc_info=True)
                    raise RuntimeError(f"Engine Failure: {e}")
    return _icgl_instance


# --- Frontend Mounting (Three Interfaces) ---
from fastapi.responses import FileResponse, JSONResponse

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional
    psutil = None

# 1. Static HTML UI Path (for docs/demos)
static_ui_path = Path(__file__).parent.parent / "ui"

# 2. React Basic UI Path (admin tools) - points to admin/dist
react_basic_path = Path(__file__).parent.parent / "admin" / "dist"

# 3. Main React App Path (production UI)
main_app_path = BASE_DIR / "web" / "dist"

# 4. Public landing path (copied to web/public)
public_path = BASE_DIR / "web" / "public"

# Workspace base for AI workspace endpoints
workspace_base = BASE_DIR / "data" / "ai_workspace"
workspace_base.mkdir(parents=True, exist_ok=True)

# Mount main React app if built
if main_app_path.exists():
    app.mount(
        "/app", StaticFiles(directory=str(main_app_path), html=True), name="main_app"
    )
    logger.info(f"✅ Main App loaded from {main_app_path}")
else:
    logger.warning(f"⚠️ Main App path not found: {main_app_path}")

# Mount React basic (admin tools) if built
if react_basic_path.exists():
    app.mount(
        "/admin",
        StaticFiles(directory=str(react_basic_path), html=True),
        name="admin_tools",
    )
    logger.info(f"✅ Admin Tools loaded from {react_basic_path}")
else:
    logger.warning(f"⚠️ Admin Tools path not found: {react_basic_path}")

# Mount static UI files
if static_ui_path.exists():
    app.mount(
        "/ui", StaticFiles(directory=str(static_ui_path), html=True), name="static_ui"
    )
    logger.info(f"✅ Static UI loaded from {static_ui_path}")
else:
    logger.warning(f"⚠️ Static UI path not found: {static_ui_path}")

# Serve landing assets from web/public (for /landing/*)
public_landing_assets = public_path / "landing"
if public_landing_assets.exists():
    app.mount(
        "/landing",
        StaticFiles(directory=str(public_landing_assets), html=True),
        name="landing_assets",
    )
    logger.info(f"✅ Landing assets loaded from {public_landing_assets}")
else:
    logger.warning(f"⚠️ Landing assets path not found: {public_landing_assets}")


# Serve landing page as root
@app.get("/")
async def serve_landing():
    """Serve unified landing page as root"""
    public_index = public_path / "index.html"
    landing_index = static_ui_path / "landing" / "index.html"
    legacy_landing = static_ui_path / "landing.html"
    if public_index.exists():
        return FileResponse(public_index)
    if landing_index.exists():
        return FileResponse(landing_index)
    if legacy_landing.exists():
        return FileResponse(legacy_landing)
    # Fallback to main app if landing doesn't exist
    return (
        FileResponse(main_app_path / "index.html")
        if main_app_path.exists()
        else {"error": "No UI found"}
    )


# --- Agents & Events Endpoints ---


@app.get("/api/events")
async def get_events():
    """Return recent system events from observability if available; fallback empty."""
    try:
        ledger = get_ledger()
        if ledger:
            events = ledger.query_events(limit=100)
            if not events:
                try:
                    icgl = get_icgl()
                    adrs = sorted(
                        icgl.kb.adrs.values(), key=lambda x: x.created_at, reverse=True
                    )
                    events = [
                        {
                            "event_type": "PROPOSAL",
                            "trace_id": adr.id,
                            "user_id": "system",
                            "timestamp": getattr(adr, "created_at", "") or "",
                            "payload": {
                                "message": f"Proposal: {adr.title}",
                                "status": adr.status,
                            },
                        }
                        for adr in adrs
                    ]
                except Exception as e:
                    logger.warning(f"Events seed from ADRs failed: {e}")
            return {
                "events": [
                    {
                        "id": f"evt-{i}",
                        "type": e.get("event_type") or e.get("type") or "SYSTEM_EVENT",
                        "message": e.get("payload", {}).get("message")
                        or e.get("message")
                        or "",
                        "timestamp": e.get("timestamp", ""),
                        "trace_id": e.get("trace_id"),
                        "user_id": e.get("user_id"),
                        "payload": e.get("payload", {}),
                        "agent": e.get("payload", {}).get("agent") or e.get("user_id"),
                    }
                    for i, e in enumerate(events)
                ]
            }
    except Exception as e:
        logger.warning(f"Events fallback (ledger error): {e}")
    return {"events": []}


# ------------------------------------------------------------------------------
# Workspace minimal support (in-memory)
# ------------------------------------------------------------------------------
_workspaces: Dict[str, Dict[str, Any]] = {}


@app.post("/api/workspaces")
async def create_workspace(payload: Dict[str, Any]):
    """
    Minimal workspace creation (in-memory).
    """
    name = payload.get("name") or "workspace"
    mode = payload.get("mode") or "NORMAL"
    workspace_id = uid()
    ws = {
        "id": workspace_id,
        "name": name,
        "mode": mode,
        "created_at": now(),
        "metadata": payload.get("metadata", {}),
    }
    _workspaces[workspace_id] = ws
    log_event(
        f"Workspace created: {name}", trace_id=workspace_id, payload={"mode": mode}
    )
    return {"workspace": ws}


@app.get("/api/workspaces")
async def list_workspaces():
    return {"workspaces": list(_workspaces.values())}


@app.get("/api/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    ws = _workspaces.get(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"workspace": ws}


# --- Governance Endpoints ---


@app.get("/api/governance/proposals")
async def get_proposals():
    """Return all ADRs/Proposals from KB."""
    try:
        icgl = get_icgl()
        adrs = list(icgl.kb.adrs.values())
        # Sort by creation time decending
        return {"proposals": sorted(adrs, key=lambda x: x.created_at, reverse=True)}
    except Exception as e:
        logger.error(f"Error listing proposals: {e}")
        return {"proposals": []}


@app.get("/api/governance/decisions")
async def get_decisions():
    """Return only approved/executed decisions."""
    try:
        icgl = get_icgl()
        adrs = [
            a
            for a in icgl.kb.adrs.values()
            if a.status in ["APPROVED", "EXECUTED", "COMPLETE"]
        ]
        return {"decisions": sorted(adrs, key=lambda x: x.created_at, reverse=True)}
    except Exception as e:
        logger.error(f"Error listing decisions: {e}")
        return {"decisions": []}


@app.post("/api/governance/decisions/register")
async def register_decision_api(req: DecisionRegisterRequest):
    """
    Registers a human decision for an ADR and persists it.
    """
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(req.proposal_id)
        if not adr:
            raise HTTPException(status_code=404, detail="ADR/Proposal not found")
        # map decision string to DecisionAction
        action_map = {
            "approved": "APPROVE",
            "approve": "APPROVE",
            "rejected": "REJECT",
            "reject": "REJECT",
            "deferred": "EXPERIMENT",
            "experiment": "EXPERIMENT",
            "modify": "MODIFY",
        }
        action_value = action_map.get(req.decision.lower(), req.decision.upper())
        decision = HumanDecision(
            id=uid(),
            adr_id=adr.id,
            action=DecisionAction(action_value),
            rationale=req.rationale,
            signed_by=req.signed_by,
            signature_hash=f"sig-{uid()}",
        )
        icgl.kb.add_human_decision(decision)
        adr.human_decision_id = decision.id
        # update adr status based on action
        if decision.action == "APPROVE":
            adr.status = "ACCEPTED"  # type: ignore
        elif decision.action == "REJECT":
            adr.status = "REJECTED"  # type: ignore
        elif decision.action == "EXPERIMENT":
            adr.status = "EXPERIMENTAL"  # type: ignore
        icgl.kb.add_adr(adr)
        log_event(
            f"Decision {decision.action} recorded for ADR {adr.id}",
            event_type=EventType.SYSTEM_EVENT,
            trace_id=adr.id,
            payload={"signed_by": req.signed_by, "rationale": req.rationale},
        )
        return {"status": "ok", "decision": decision.__dict__, "adr": adr.__dict__}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Decision registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/governance/timeline")
async def get_governance_timeline():
    """Return a timeline of governance events."""
    try:
        icgl = get_icgl()
        # For now, derive from ADRs and internal events
        events = []
        for adr in icgl.kb.adrs.values():
            events.append(
                {
                    "id": f"evt-{adr.id}",
                    "type": "adr",
                    "title": adr.title,
                    "status": adr.status,
                    "timestamp": adr.created_at,
                }
            )
        return {"timeline": sorted(events, key=lambda x: x["timestamp"], reverse=True)}
    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        return {"timeline": []}


@app.get("/api/governance/conflicts")
async def get_conflicts():
    """Return stored conflicts (in-memory placeholder)."""
    return {"conflicts": _conflicts, "status": "ok"}


@app.post("/api/governance/conflicts")
async def create_conflict(conflict: Dict[str, Any]):
    """Create a conflict entry (in-memory placeholder)."""
    try:
        new_conflict = {
            "id": conflict.get("id") or uid(),
            "title": conflict.get("title", "Untitled conflict"),
            "description": conflict.get("description", ""),
            "proposals": conflict.get("proposals", []),
            "involved_agents": conflict.get("involved_agents", []),
            "state": conflict.get("state", "open"),
            "created_at": now(),
            "updated_at": now(),
            "comments": conflict.get("comments", []),
            "resolution": conflict.get("resolution"),
        }
        _conflicts.append(new_conflict)
        log_event(
            f"Conflict created: {new_conflict['id']}",
            event_type=EventType.SYSTEM_EVENT,
            trace_id=new_conflict["id"],
            payload={"title": new_conflict["title"], "state": new_conflict["state"]},
        )
        return {"status": "ok", "conflict": new_conflict}
    except Exception as e:
        logger.error(f"Create conflict error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/terminal")
async def run_terminal(req: TerminalRequest):
    """
    Execute terminal command via EngineerAgent.
    """
    try:
        icgl = get_icgl()
        if not icgl.engineer:
            return {"error": "EngineerAgent not active", "status": "error", "code": 503}

        result = icgl.engineer.run_terminal(req.cmd, req.path)
        log_event(
            f"Terminal command executed: {req.cmd[:50]}",
            event_type=EventType.SYSTEM_EVENT,
            payload={"cmd": req.cmd, "status": result.get("status")},
        )
        return result
    except Exception as e:
        logger.error(f"Terminal execution error: {e}")
        return {"error": str(e), "status": "error", "code": 500}


@app.post("/api/chat/file/write")
async def write_file_api(req: FileWriteRequest):
    """
    Write file to disk via EngineerAgent.
    """
    try:
        icgl = get_icgl()
        if not icgl.engineer:
            return {"error": "EngineerAgent not active", "status": "error", "code": 503}

        res = icgl.engineer.write_file(req.path, req.content, req.mode)
        log_event(
            f"File written to disk: {req.path}",
            event_type=EventType.SYSTEM_EVENT,
            payload={"path": req.path, "mode": req.mode},
        )

        if "Success" in res:
            return {
                "status": "success",
                "path": req.path,
                "message": f"Successfully written to {req.path}",
            }
        else:
            return {"status": "error", "message": res, "path": req.path}

    except Exception as e:
        logger.error(f"File write error: {e}")
        return {"error": str(e), "status": "error", "code": 500}


@app.post("/api/governance/approve-changes")
async def approve_changes_api(req: Dict[str, str]):
    """
    Final approval stage: Executes the previously synthesized changes.
    """
    adr_id = req.get("adr_id")
    if not adr_id or adr_id not in active_synthesis:
        raise HTTPException(
            status_code=404, detail="Pending changes not found for this ADR"
        )

    synthesis_data = active_synthesis[adr_id]["synthesis"]
    icgl = get_icgl()
    eng = getattr(icgl, "engineer", None)

    if not eng:
        raise HTTPException(
            status_code=503, detail="EngineerAgent not available for execution"
        )

    applied = []
    errors = []

    # Extract file changes from all agent results
    for agent_res in synthesis_data.get("agent_results", []):
        fc_list = agent_res.get("file_changes", [])
        for fc in fc_list:
            path = fc.get("path")
            content = fc.get("content")
            mode = fc.get("mode", "w")

            # Normalize path (simplified for this endpoint)
            # Note: In a production system, use the same path resolution logic as synthesis
            try:
                res = eng.write_file(path, content, mode)
                applied.append({"path": path, "result": res})
            except Exception as e:
                errors.append({"path": path, "error": str(e)})

    # Update state
    synthesis_data["applied_changes"] = applied
    synthesis_data["status"] = "complete"

    # Log event
    log_event(
        f"Human approved and applied {len(applied)} changes for ADR {adr_id}",
        event_type=EventType.SYSTEM_EVENT,
        trace_id=adr_id,
        payload={"applied": applied, "errors": errors},
    )

    return {"status": "success", "applied": applied, "errors": errors}


@app.get("/api/governance/adr/latest")
async def get_latest_adr_api():
    """Alias for /status-like latest ADR fetch."""
    try:
        icgl = get_icgl()
        adrs = list(icgl.kb.adrs.values())
        if not adrs:
            return {}
        latest = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]
        return latest.__dict__
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/idea-summary/{adr_id}")
async def get_idea_summary(adr_id: str):
    """Return summary for a given ADR from KB if available."""
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(adr_id)
        if not adr:
            return {
                "adr_id": adr_id,
                "status": "not_found",
                "message": "No ADR found. Create a proposal to start analysis.",
            }
        # naive summary generation from context/decision
        summary = (adr.decision or adr.context or "").strip()
        if len(summary) > 240:
            summary = summary[:240] + "..."
        return {
            "adr_id": adr.id,
            "title": adr.title,
            "context": adr.context,
            "decision": adr.decision,
            "status": adr.status,
            "signals": adr.sentinel_signals,
            "summary": summary or "No summary available yet.",
            "idea": adr.context.splitlines()[0] if adr.context else adr.title,
        }
    except Exception as e:
        logger.error(f"Idea summary error: {e}")
        return {"adr_id": adr_id, "status": "error", "message": str(e)}


# --- State ---
active_synthesis: Dict[str, Any] = {}
global_telemetry = {"drift_detection_count": 0, "agent_failure_count": 0}


# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSocket clients."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                # Connection closed, mark for removal
                dead_connections.append(connection)
            except Exception as e:
                logger.warning(f"Broadcast error: {e}")

        # Clean up dead connections
        for conn in dead_connections:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


# --- Diagnostic Endpoints ---


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Diagnostic endpoint to verify system sanity."""
    health: Dict[str, Any] = {
        "integrity_score": 95,
        "status": "normal",
        "active_agents": 0,
        "active_operations": 0,
        "waiting_for_human": False,
    }

    # System metrics
    if psutil:
        try:
            health["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            health["memory_percent"] = psutil.virtual_memory().percent
            health["disk_percent"] = psutil.disk_usage("/").percent
        except Exception:
            pass

    try:
        icgl = get_icgl()
        health["active_agents"] = len(icgl.registry.list_agents())
        # Active operations ~ events count in ledger
        from backend.observability import get_ledger

        ledger = get_ledger()
        if ledger:
            health["active_operations"] = len(ledger.query_events(limit=20))
        # Waiting for human if any ADR in DRAFT
        adrs = list(icgl.kb.adrs.values())
        health["waiting_for_human"] = any(
            getattr(a, "status", "") == "DRAFT" for a in adrs
        )
    except Exception as e:
        health["status"] = "degraded"
        health["error"] = str(e)

    return health


@app.get("/status")
async def get_status() -> Dict[str, Any]:
    try:
        icgl = get_icgl()
        last_adr = None
        adrs = list(icgl.kb.adrs.values())
        if adrs:
            last_adr = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]

        # Calculate Alert Level
        alert_level = "NONE"
        last_latency = 0

        if last_adr and last_adr.sentinel_signals:
            if any("🚨" in s or "CRITICAL" in s for s in last_adr.sentinel_signals):
                alert_level = "CRITICAL"
            elif any("⚠️" in s or "WARNING" in s for s in last_adr.sentinel_signals):
                alert_level = "HIGH"

        if last_adr and last_adr.id in active_synthesis:
            last_latency = active_synthesis[last_adr.id].get("latency_ms", 0)

        return {
            "mode": "COCKPIT",
            "waiting_for_human": last_adr.status == "DRAFT" if last_adr else False,
            "active_alert_level": alert_level,
            "last_adr_id": last_adr.id if last_adr else None,
            "telemetry": {**global_telemetry, "last_latency_ms": last_latency},
        }
    except Exception as e:
        return {"mode": "ERROR", "error": str(e)}


@app.post("/propose")
async def propose_decision(req: ProposalRequest, background_tasks: BackgroundTasks):
    logger.info(f"📝 Proposal Received: {req.title}")
    try:
        icgl = get_icgl()
        adr = ADR(
            id=uid(),
            title=req.title,
            status="DRAFT",
            context=req.context,
            decision=req.decision,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )

        icgl.kb.add_adr(adr)
        active_synthesis[adr.id] = {"status": "processing"}

        background_tasks.add_task(run_analysis_task, adr, req.human_id)
        log_event(
            f"Proposal created: {adr.title}",
            event_type=EventType.SYSTEM_EVENT,
            trace_id=adr.id,
            payload={"status": adr.status, "human_id": req.human_id},
        )
        return {"status": "Analysis Triggered", "adr_id": adr.id}
    except Exception as e:
        logger.error(f"Proposal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/governance/proposals/create")
async def create_proposal_api(req: ProposalRequest, background_tasks: BackgroundTasks):
    """
    UI alias to /propose. Uses same governed flow.
    """
    return await propose_decision(req, background_tasks)


@app.patch("/api/governance/proposals/{proposal_id}")
async def patch_proposal_api(proposal_id: str, payload: Dict[str, Any]):
    """
    Basic proposal patching: currently supports status update only.
    """
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(proposal_id)
        if not adr:
            raise HTTPException(status_code=404, detail="Proposal not found")
        new_state = payload.get("state")
        if new_state:
            allowed = {"DRAFT", "CONDITIONAL", "ACCEPTED", "REJECTED", "EXPERIMENTAL"}
            state_upper = str(new_state).upper()
            if state_upper not in allowed:
                raise HTTPException(status_code=400, detail="Invalid state value")
            adr.status = state_upper  # type: ignore
            icgl.kb.add_adr(adr)  # persist
            log_event(
                f"Proposal {adr.id} state updated to {state_upper}",
                event_type=EventType.SYSTEM_EVENT,
                trace_id=adr.id,
                payload={"state": state_upper},
            )
        return {"proposal": adr.__dict__, "status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Patch proposal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/idea-run")
async def idea_run(req: IdeaRequest, background_tasks: BackgroundTasks):
    """
    Fast path: take freeform idea text, wrap it as an ADR, and trigger full ICGL (with auto-approve if enabled).
    """
    idea = req.idea.strip()
    if not idea:
        raise HTTPException(status_code=400, detail="Idea text is required.")

    title = idea[:80] + ("..." if len(idea) > 80 else "")
    logger.info(f"🚀 Idea Received: {title}")
    try:
        icgl = get_icgl()
        adr = ADR(
            id=uid(),
            title=title or "Idea Run",
            status="DRAFT",
            context=idea,
            decision=idea,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        target_files = resolve_targets_from_text(idea)

        # DEBUG: Log what we found
        logger.info(f"📍 Idea text: {idea[:100]}...")
        logger.info(f"📍 Resolved {len(target_files)} target files: {target_files}")
        logger.info(f"📍 Path map has {len(load_path_map())} entries")

        icgl.kb.add_adr(adr)
        active_synthesis[adr.id] = {
            "status": "processing",
            "mode": "idea-run",
            "target_files": target_files,
        }

        background_tasks.add_task(
            run_analysis_task, adr, req.human_id, target_files=target_files
        )
        return {"status": "Analysis Triggered", "adr_id": adr.id}
    except Exception as e:
        logger.error(f"Idea Run Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Aliases under /api prefix for proxy compatibility
@app.post("/api/idea-run")
async def idea_run_api(req: IdeaRequest, background_tasks: BackgroundTasks):
    return await idea_run(req, background_tasks)


@app.post("/api/governance/clarify")
async def governance_clarify(req: Dict[str, Any], background_tasks: BackgroundTasks):
    """Resumes an analysis task with clarified context from the human sovereign."""
    adr_id = req.get("adr_id")
    answer = req.get("answer")
    human_id = req.get("human_id", "anonymous")

    icgl = get_icgl()
    adr = icgl.kb.get_adr(adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")

    # Append the clarification to the context
    adr.context += f"\n\n[Clarification provided by Human]: {answer}"

    # Restart the background task
    # We might need to find target_files from previous run or ADR metadata
    target_files = []  # In a real system, we'd retrieve this from the active_synthesis state
    if adr_id in active_synthesis:
        target_files = active_synthesis[adr_id].get("target_files", [])

    background_tasks.add_task(
        run_analysis_task, adr, human_id, target_files=target_files
    )
    return {"status": "Analysis Resumed", "adr_id": adr.id}


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, we primarily broadcast to them
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/analysis/{adr_id}")
async def websocket_analysis(websocket: WebSocket, adr_id: str):
    """WebSocket endpoint for real-time analysis updates."""
    await websocket.accept()
    try:
        while True:
            if adr_id in active_synthesis:
                await websocket.send_json(active_synthesis[adr_id])
                if (
                    active_synthesis[adr_id].get("status") == "complete"
                    or "synthesis" in active_synthesis[adr_id]
                ):
                    break  # Done
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from analysis/{adr_id}")
    except Exception as e:
        logger.warning(f"Error in analysis stream for {adr_id}: {e}")
        try:
            await websocket.send_json(
                {"error": "Analysis stream error", "message": str(e)}
            )
        except Exception:
            pass  # Client already gone
    finally:
        try:
            await websocket.close()
        except Exception:
            pass  # Already closed


async def run_analysis_task(
    adr: ADR, human_id: str, target_files: Optional[List[str]] = None
) -> None:
    """Background task to run full ICGL analysis on an ADR."""
    start_time = time.time()
    logger.info(f"🌀 Starting Background Analysis for {adr.id}")
    try:
        icgl = get_icgl()
        from backend.agents.base import Problem

        # Policy gate check (pre-analysis)
        policy_report = icgl.enforcer.check_adr_compliance(adr)
        if policy_report.status == "FAIL":
            active_synthesis[adr.id] = {
                "status": "blocked",
                "policy_report": policy_report.__dict__,
            }
            return

        # 1. Semantic Search (Historical Echo / S-11)
        query = f"{adr.title} {adr.context} {adr.decision}"
        matches = []
        mem = getattr(icgl, "memory", None)
        if mem is not None and hasattr(mem, "search"):
            try:
                matches = await mem.search(query, limit=4)
            except Exception as e:
                logger.warning(f"Semantic search skipped: {e}")
        semantic = []
        for m in matches:
            if m.document.id != adr.id:
                semantic.append(
                    {
                        "id": m.document.id,
                        "title": m.document.metadata.get("title", "Unknown"),
                        "score": round(m.score * 100, 1),
                    }
                )

        # 2. Sentinel Detailed Scan
        alerts = await icgl.sentinel.scan_adr_detailed_async(adr, icgl.kb)
        if any(a.category.value == "Drift" for a in alerts):
            global_telemetry["drift_detection_count"] += 1

        # 3. Agent Synthesis Context (Load Target Files)
        logger.info(f"📁 Loading {len(target_files or [])} target file contents...")
        contents: Dict[str, str] = {}
        import os

        project_root = Path(os.getcwd())

        if target_files:
            for tf in target_files:
                try:
                    path = project_root / tf if not Path(tf).is_absolute() else Path(tf)
                    if path.exists():
                        content = path.read_text(encoding="utf-8")
                        contents[tf] = content
                        logger.info(f"  ✅ Loaded {len(content)} chars from {tf}")
                except Exception as e:
                    logger.error(f"  ❌ Error loading {tf}: {e}")

        problem = Problem(
            title=adr.title,
            context=adr.context,
            metadata={
                "decision": adr.decision,
                "target_files": target_files or [],
                "file_contents": contents,
            },
        )

        # 4. SEQUENTIAL AGENT COLLABORATION (Sovereign Clarity Loop)
        agent_results = []

        # --- PHASE A: ARCHITECT (Clarity Gate) ---
        logger.info("🧠 Phase A: Architect Analysis...")
        architect_res = await icgl.architect.analyze(problem, icgl.kb)
        agent_results.append(architect_res)

        if architect_res.clarity_needed:
            logger.warning(
                f"⚠️ Clarity required for {adr.id}: {architect_res.clarity_question}"
            )
            active_synthesis[adr.id] = {
                "status": "clarity_required",
                "question": architect_res.clarity_question,
                "agent": "Architect",
                "agent_results": [
                    asdict(r) for r in agent_results if hasattr(r, "agent_id")
                ],
                "timestamp": time.time(),
            }
            return

        # Layer 1: Inject Intent into Problem for specialists
        if architect_res.intent:
            problem.intent = architect_res.intent
            logger.info(
                f"📜 Intent Contract generated: {problem.intent.goal} (Risk: {problem.intent.risk_level})"
            )

        # --- PHASE B: SPECIALISTS (Understanding Gate) ---
        logger.info("🔬 Phase B: Specialist Review...")
        risk_level = (problem.intent.risk_level if problem.intent else "medium").lower()

        specialists = [
            getattr(icgl, "failure", None),
            getattr(icgl, "designer", None),
            getattr(icgl, "concept_guardian", None),
        ]
        specialists = [s for s in specialists if s]

        # Fast Track for Low Risk
        if risk_level == "low":
            logger.info("🚀 Fast Track enabled for low-risk change.")
            # Run only one relevant specialist or just Builder
            if specialists:
                res = await specialists[0].analyze(problem, icgl.kb)
                agent_results.append(res)
        else:
            # Full Track: Run all specialists and check Understanding Gate
            for s in specialists:
                res = await s.analyze(problem, icgl.kb)
                agent_results.append(res)

            # Layer 2 Check: Understanding Conflict or Low Confidence
            confidences = [
                r.understanding.get("confidence", 0.0)
                for r in agent_results
                if r.understanding
            ]
            needs_mediation = any(c < 0.7 for c in confidences)

            if needs_mediation:
                logger.info("⚖️ Low confidence detected. Invoking Mediator...")
                mediator = getattr(icgl, "mediator", None)
                if mediator:
                    # Pass results to mediator context
                    problem.metadata["agent_results"] = [
                        {
                            "agent_id": r.agent_id,
                            "understanding": r.understanding,
                            "confidence": r.confidence,
                        }
                        for r in agent_results
                    ]
                    mediation_res = await mediator.analyze(problem, icgl.kb)
                    agent_results.append(mediation_res)

                    if mediation_res.clarity_needed:
                        logger.warning("✋ Mediator escalated to Clarity required.")
                        active_synthesis[adr.id] = {
                            "status": "clarity_required",
                            "question": mediation_res.clarity_question,
                            "agent": "Mediator",
                            "agent_results": [
                                asdict(r)
                                for r in agent_results
                                if hasattr(r, "agent_id")
                            ],
                            "timestamp": time.time(),
                        }
                        return

        # --- PHASE C: BUILDER (Implementation) ---
        logger.info("🏗️ Phase C: Builder Implementation...")
        # Inject Micro-Examples if available (Layer 3)
        if problem.intent and problem.intent.micro_examples:
            problem.context += (
                f"\n\nLAYER 3 - MICRO-EXAMPLES:\n{problem.intent.micro_examples}"
            )

        problem.metadata["architect_plan"] = architect_res.analysis
        builder_res = await icgl.builder.analyze(problem, icgl.kb)
        agent_results.append(builder_res)

        # --- PHASE D: SENTINEL (Context Integrity Check) ---
        logger.info("🛡️ Phase D: Sentinel Integrity Check...")
        adr.file_changes = builder_res.file_changes
        # Pass intent to ADR for Rule S-20 (Layer 1 enforcement)
        if problem.intent:
            from dataclasses import asdict

            adr.intent = asdict(problem.intent)

        final_alerts = await icgl.sentinel.scan_adr_detailed_async(adr, icgl.kb)

        # 5. FINAL SYNTHESIS & STAGING
        latency = (time.time() - start_time) * 1000
        from dataclasses import asdict

        active_synthesis[adr.id] = {
            "adr": asdict(adr),
            "status": "complete",
            "adr_id": adr.id,
            "synthesis": {
                "agent_results": [
                    asdict(r) for r in agent_results if hasattr(r, "agent_id")
                ],
                "overall_confidence": min([r.confidence for r in agent_results])
                if agent_results
                else 0.0,
                "consensus_recommendations": architect_res.recommendations,
                "all_concerns": [c for r in agent_results for c in r.concerns],
                "sentinel_alerts": [
                    {
                        "id": a.rule_id,
                        "severity": a.severity.value,
                        "message": a.message,
                        "category": a.category.value,
                    }
                    for a in final_alerts
                ],
                "integrity_blocked": any(
                    a.severity.value == "CRITICAL" for a in final_alerts
                ),
                "policy_report": policy_report.__dict__,
                "applied_changes": [],
                "target_files": target_files or [],
            },
            "latency_ms": latency,
            "timestamp": time.time(),
        }
        logger.info(f"✅ Analysis for {adr.id} complete and STAGED in {latency:.0f}ms")

        # Persist event log
        try:
            log_idea_event(
                adr_id=adr.id,
                idea=adr.context,
                target_files=target_files or [],
                applied=[],
                skipped=[fc.path for fc in builder_res.file_changes],
            )
        except Exception as e:
            logger.warning(f"Failed to log idea run: {e}")

        # FINAL BROADCAST
        await manager.broadcast({"type": "status_update", "status": await get_status()})

        # Update ADR in KB
        adr.sentinel_signals = [str(a) for a in final_alerts]
        icgl.kb.add_adr(adr)

        logger.info(f"✨ Analysis Complete for {adr.id}")
        return active_synthesis[adr.id]
    except Exception as e:
        global_telemetry["agent_failure_count"] += 1
        logger.error(f"Async Analysis Failure: {e}", exc_info=True)
        active_synthesis[adr.id] = {"status": "failed", "error": str(e)}
        return active_synthesis[adr.id]


@app.get("/analysis/{adr_id}")
async def get_analysis(adr_id: str) -> Dict[str, Any]:
    if adr_id in active_synthesis:
        return active_synthesis[adr_id]
    # Fallback: derive a lightweight analysis from ADR data so UI has something to render
    icgl = get_icgl()
    adr = icgl.kb.get_adr(adr_id)
    if not adr:
        raise HTTPException(
            status_code=404, detail="Analysis session context lost or not started."
        )
    derived = {
        "adr_id": adr.id,
        "status": adr.status or "UNKNOWN",
        "message": f"Derived analysis for ADR {adr.title}",
        "analysis": {
            "adr_id": adr.id,
            "title": adr.title,
            "stages": [
                {
                    "name": "Context",
                    "items": [
                        {
                            "title": adr.context or "No context",
                            "status": "done",
                            "owner": "system",
                        }
                    ],
                },
                {
                    "name": "Decision",
                    "items": [
                        {
                            "title": adr.decision or "No decision",
                            "status": "done",
                            "owner": "system",
                        }
                    ],
                },
            ],
        },
    }
    active_synthesis[adr.id] = derived
    return derived


@app.get("/api/analysis/latest")
async def get_latest_analysis():
    icgl = get_icgl()
    adrs = list(icgl.kb.adrs.values())
    if not adrs:
        return {
            "status": "empty",
            "message": "No ADRs found. Please propose a new decision to start analysis.",
            "analysis": None,
        }
    last_adr = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]
    if last_adr.id not in active_synthesis:
        # Seed a lightweight analysis so UI has something to render
        seeded = {
            "adr_id": last_adr.id,
            "status": "ready",
            "message": f"Analysis seeded for ADR {last_adr.title}",
            "analysis": {
                "adr_id": last_adr.id,
                "title": last_adr.title,
                "stages": [
                    {
                        "name": "Context",
                        "items": [
                            {"title": "Problem", "status": "done", "owner": "system"}
                        ],
                    },
                    {
                        "name": "Assessment",
                        "items": [
                            {
                                "title": "Initial review",
                                "status": "done",
                                "owner": "system",
                            }
                        ],
                    },
                ],
            },
        }
        active_synthesis[last_adr.id] = seeded
        return seeded
    return await get_analysis(last_adr.id)


@app.get("/api/analysis/{adr_id}")
async def get_analysis_api(adr_id: str) -> Dict[str, Any]:
    return await get_analysis(adr_id)


@app.get("/system/agents")
@app.get("/api/system/agents")
async def list_agents():
    """
    Lists registered agents to satisfy frontend fetches with rich metadata.
    """
    try:
        icgl = get_icgl()
        agents = icgl.registry.list_agents()
        try:
            from backend.agents.metadata import get_agent_metadata

            return {
                "agents": [
                    get_agent_metadata(a.value if hasattr(a, "value") else str(a))
                    for a in agents
                ]
            }
        except Exception as meta_err:
            logger.error(f"Agent metadata error: {meta_err}", exc_info=True)
    except Exception as e:
        logger.error(f"List agents error: {e}", exc_info=True)
    # Always fallback: return dummy agent list for frontend
    return {
        "agents": [
            {
                "id": "dummy-agent",
                "name": "Dummy Agent",
                "description": "Fallback agent entry due to backend error.",
                "status": "ERROR",
            }
        ]
    }


@app.post("/api/system/agents/{agent_id}/run")
async def run_agent_api(agent_id: str, req: AgentRunRequest):
    """
    Run a specific agent by id. Returns the AgentResult shape or 404/400.
    """
    try:
        icgl = get_icgl()
        # Map agent_id string to AgentRole if possible
        from backend.agents.base import AgentRole

        try:
            role = AgentRole(agent_id)
        except Exception:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Unknown agent role '{agent_id}'",
                },
            )

        problem = Problem(
            title=req.title, context=req.context, metadata={"source": "api"}
        )
        result = await icgl.registry.run_agent(role, problem, icgl.kb)
        if result is None:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "not_found",
                    "message": f"Agent '{agent_id}' not registered",
                },
            )

        def serialize_result(res):
            data = res.__dict__.copy()
            if hasattr(data.get("role"), "value"):
                data["role"] = data["role"].value
            return data

        return {"status": "ok", "agent": agent_id, "result": serialize_result(result)}
    except Exception as e:
        logger.error(f"Run agent error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


@app.post("/sign/{adr_id}")
async def sign_decision(adr_id: str, req: SignRequest):
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(adr_id)
        if not adr:
            raise HTTPException(status_code=404, detail="ADR not found")

        result_data = active_synthesis.get(adr_id)
        if not result_data or "synthesis" not in result_data:
            raise HTTPException(status_code=400, detail="Synthesis data missing.")

        # Block on policy or sentinel critical
        pol = result_data["synthesis"].get("policy_report")
        if pol and pol.get("status") == "FAIL":
            raise HTTPException(
                status_code=400, detail="Policy gate failed; cannot sign."
            )
        alerts = result_data["synthesis"].get("sentinel_alerts") or []
        if any(a.get("severity") == "CRITICAL" for a in alerts):
            raise HTTPException(
                status_code=400, detail="Critical sentinel alert; cannot sign."
            )

        # Record Decision
        # Coerce action to DecisionAction literal when possible
        action_val = req.action.upper() if isinstance(req.action, str) else req.action
        decision = icgl.hdal.sign_decision(
            adr_id, cast(DecisionAction, action_val), req.rationale, req.human_id
        )

        # Persistence
        adr.status = "ACCEPTED" if req.action == "APPROVE" else "REJECTED"
        adr.human_decision_id = decision.id
        icgl.kb.add_adr(adr)
        icgl.kb.add_human_decision(decision)

        # Execution (Cycle 9)
        auto_write_enabled = is_auto_write_enabled()
        if (
            req.action == "APPROVE"
            and getattr(icgl, "engineer", None)
            and auto_write_enabled
        ):
            all_changes = []
            for res in result_data["synthesis"]["agent_results"]:
                if "file_changes" in res and res["file_changes"]:
                    from backend.kb.schemas import FileChange

                    for fc in res["file_changes"]:
                        change_data = {
                            "path": fc.get("path"),
                            "content": fc.get("content"),
                            "action": fc.get("action", "CREATE"),
                        }
                        all_changes.append(FileChange(**change_data))

            if all_changes:
                eng = getattr(icgl, "engineer", None)
                if eng is not None and hasattr(eng, "write_file"):
                    for change in all_changes:
                        eng.write_file(change.path, change.content)
                    if hasattr(eng, "commit_decision"):
                        eng.commit_decision(adr, decision)
                else:
                    logger.warning(
                        "Auto-apply requested but no engineer available; skipping file writes."
                    )

        elif (
            req.action == "APPROVE"
            and getattr(icgl, "engineer", None)
            and not auto_write_enabled
        ):
            logger.info(
                "⚠️ Auto-write/commit disabled (ICGL_ENABLE_AUTO_WRITE not set). Skipping execution."
            )

        return {"status": "Complete", "action": req.action}
    except Exception as e:
        logger.error(f"Sign Failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kb/{type}")
async def list_kb(type: str) -> Any:
    try:
        icgl = get_icgl()
        if type == "adrs":
            return sorted(
                list(icgl.kb.adrs.values()), key=lambda x: x.created_at, reverse=True
            )
        if type == "policies":
            return list(icgl.kb.policies.values())
        return {"error": "Invalid KB type"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/kb/adr/{adr_id}")
async def delete_adr(adr_id: str) -> Dict[str, Any]:
    try:
        icgl = get_icgl()
        removed = icgl.kb.remove_adr(adr_id)
        if not removed:
            raise HTTPException(status_code=404, detail="ADR not found")
        return {"status": "deleted", "adr_id": adr_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_consensus_mindmap(title: str, synthesis) -> str:
    """Generates Mermaid mindmap syntax from synthesis results."""
    lines: List[str] = ["mindmap", f"  root(({title}))"]

    # Consensus Node
    lines.append("    Consensus")
    for rec in synthesis.consensus_recommendations[:3]:
        # Clean text for Mermaid (no special chars)
        clean_rec = rec.replace("(", "[").replace(")", "]").replace('"', "'")
        lines.append(f"      {clean_rec}")

    # Agents Node
    lines.append("    Agents")
    for res in synthesis.individual_results:
        role = res.role.value
        conf = int(res.confidence * 100)
        lines.append(f"      {role} ({conf}%)")
        if res.concerns:
            first_concern = res.concerns[0].replace("(", "[").replace(")", "]")
            lines.append(f"        {first_concern}")

    # Risks Node
    if synthesis.all_concerns:
        lines.append("    Risks")
        for concern in synthesis.all_concerns[:3]:
            clean_concern = concern.replace("(", "[").replace(")", "]")
            lines.append(f"      {clean_concern}")

    return "\n".join(lines)


# -----------------------------------------------------------------------------
# 🔒 Runtime Guardrails Helpers
# -----------------------------------------------------------------------------


def is_auto_write_enabled() -> bool:
    """Check if auto write/commit is explicitly enabled by environment."""
    return os.getenv("ICGL_ENABLE_AUTO_WRITE", "").lower() in {"1", "true", "yes"}


# =============================================================================
# 💬 CHAT ENDPOINT (Conversational Interface)
# =============================================================================

from backend.chat import ConversationOrchestrator
from backend.chat.schemas import ChatRequest, ChatResponse

# Initialize chat orchestrator (uses governed ICGL + Runtime Guard)
chat_orchestrator = ConversationOrchestrator(get_icgl, run_analysis_task)
chat_ws_manager = ConnectionManager()


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Conversational interface endpoint.

    User sends natural language message, system responds with rich structured content.
    """
    try:
        logger.info(f"💬 Chat message: {request.message[:80]}...")
        normalized = request.message.strip().lower()
        if normalized in {"approve_recommendations", "reject_recommendations"}:
            action = "APPROVE" if "approve" in normalized else "REJECT"
            response = chat_orchestrator.composer.recommendations_receipt(
                action, {"mode": "explore"}
            )
            response.state["session_id"] = request.session_id
            try:
                await chat_ws_manager.broadcast(jsonable_encoder(response))
            except Exception as e:
                logger.warning(f"Chat broadcast failed: {e}")
            return response

        if "recommendation" in normalized and any(
            word in normalized
            for word in [
                "approve",
                "reject",
                "accept",
                "decline",
                "وافق",
                "ارفض",
                "قبول",
                "رفض",
            ]
        ):
            action = (
                "APPROVE"
                if any(
                    word in normalized for word in ["approve", "accept", "وافق", "قبول"]
                )
                else "REJECT"
            )
            response = chat_orchestrator.composer.recommendations_receipt(
                action, {"mode": "explore"}
            )
            response.state["session_id"] = request.session_id
            try:
                await chat_ws_manager.broadcast(jsonable_encoder(response))
            except Exception as e:
                logger.warning(f"Chat broadcast failed: {e}")
            return response

        response = await chat_orchestrator.handle(request)
        if any(
            "Unrecognized intent" in (msg.content or "") for msg in response.messages
        ):
            if normalized in {"approve_recommendations", "reject_recommendations"} or (
                "recommendation" in normalized
                and any(
                    word in normalized
                    for word in [
                        "approve",
                        "reject",
                        "accept",
                        "decline",
                        "وافق",
                        "ارفض",
                        "قبول",
                        "رفض",
                    ]
                )
            ):
                action = (
                    "APPROVE"
                    if any(
                        word in normalized
                        for word in ["approve", "accept", "وافق", "قبول"]
                    )
                    else "REJECT"
                )
                response = chat_orchestrator.composer.recommendations_receipt(
                    action, {"mode": "explore"}
                )
                response.state["session_id"] = request.session_id
        # Broadcast to connected chat clients (stateful viewers)
        try:
            await chat_ws_manager.broadcast(jsonable_encoder(response))
        except Exception as e:
            logger.warning(f"Chat broadcast failed: {e}")
        return response
    except Exception as e:
        logger.error(f"[chat_endpoint] Exception: {e}\n{traceback.format_exc()}")
        return chat_orchestrator.composer.error(f"Chat endpoint failed: {e}")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await chat_ws_manager.connect(websocket)
    try:
        # Initial handshake: send empty chat state so first frame includes `messages`
        await websocket.send_json(
            {
                "messages": [],
                "state": {
                    "mode": "explore",
                    "waiting_for_human": False,
                    "session_id": None,
                },
            }
        )
        # Lightweight ack for UI consoles
        await websocket.send_json(
            {"type": "stream", "content": "Connected via Secure Uplink."}
        )

        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                user_content = data.get("content", "")
                normalized = user_content.strip().lower()
                if normalized in {
                    "approve_recommendations",
                    "reject_recommendations",
                } or (
                    "recommendation" in normalized
                    and any(
                        word in normalized
                        for word in [
                            "approve",
                            "reject",
                            "accept",
                            "decline",
                            "وافق",
                            "ارفض",
                            "قبول",
                            "رفض",
                        ]
                    )
                ):
                    action = (
                        "APPROVE"
                        if any(
                            word in normalized
                            for word in ["approve", "accept", "وافق", "قبول"]
                        )
                        else "REJECT"
                    )
                    response = chat_orchestrator.composer.recommendations_receipt(
                        action, {"mode": "explore"}
                    )
                    for msg in response.messages:
                        if msg.role == "assistant" and msg.content:
                            await websocket.send_json(
                                {"type": "stream", "content": msg.content}
                            )
                    if response.state:
                        await websocket.send_json(
                            {"type": "state", "state": response.state}
                        )
                    continue

                # Create a mock Request object since Orchestrator expects one
                chat_req = ChatRequest(message=user_content)

                # Signal "Thinking" - Let frontend know we are working on it
                await websocket.send_json({"type": "stream", "content": "..."})

                logger.info(f"⏳ Processing Chat Request: {user_content[:50]}...")
                start_ts = time.time()

                try:
                    # Process via Orchestrator with timeout safety
                    response = await asyncio.wait_for(
                        chat_orchestrator.handle(chat_req), timeout=25.0
                    )
                except asyncio.TimeoutError:
                    logger.error("❌ Orchestrator Timeout (25s)")
                    await websocket.send_json(
                        {
                            "type": "stream",
                            "content": "⚠️ System Timeout: Core reasoning took too long. Please try a simpler request.",
                        }
                    )
                    continue

                duration = time.time() - start_ts
                logger.info(f"✅ Chat Processed in {duration:.2f}s")

                # Send text response(s) from assistant messages
                for msg in response.messages:
                    if msg.role == "assistant":
                        # Stream text
                        if msg.content:
                            await websocket.send_json(
                                {"type": "stream", "content": msg.content}
                            )

                        # Send blocks
                        if msg.blocks:
                            for block in msg.blocks:
                                await websocket.send_json(
                                    {
                                        "type": "block",
                                        "block_type": block.type,
                                        "title": block.title,
                                        "content": block.data,
                                    }
                                )

                # Send state for UI actions (e.g., approval required)
                if response.state:
                    await websocket.send_json(
                        {"type": "state", "state": response.state}
                    )

            except json.JSONDecodeError:
                pass
            except Exception as e:
                logger.error(f"WS Handling Error: {e}")
                await websocket.send_json(
                    {"type": "stream", "content": f"System Error: {str(e)}"}
                )

    except WebSocketDisconnect:
        chat_ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"Chat WS error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
        chat_ws_manager.disconnect(websocket)


# =============================================================================
# 📊 OBSERVABILITY ENDPOINTS (Phase 1: Read-Only)
# =============================================================================


@app.get("/observability/stats")
async def get_observability_stats():
    """Get observability ledger statistics"""
    try:
        from backend.observability import get_ledger

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        return ledger.get_stats()
    except Exception as e:
        logger.error(f"Observability stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/traces")
async def list_recent_traces(limit: int = 50):
    """List recent traces with metadata"""
    try:
        from backend.observability import get_ledger

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        traces = ledger.get_recent_traces(limit=limit)
        return {"traces": traces, "count": len(traces)}
    except Exception as e:
        logger.error(f"List traces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/trace/{trace_id}")
async def get_trace_details(trace_id: str):
    """Get complete trace for replay"""
    try:
        from backend.observability import get_ledger

        ledger = get_ledger()
        if not ledger:
            pass
            return {"error": "Observability not initialized"}
        events = ledger.get_trace(trace_id)
        return {
            "trace_id": trace_id,
            "event_count": len(events),
            "events": [e.to_dict() for e in events],
        }
    except Exception as e:
        logger.error(f"Get trace error: {e}")


@app.get("/observability/trace/{trace_id}/graph")
async def get_trace_graph(trace_id: str):
    """Get trace visualization graph"""
    try:
        from backend.observability import get_ledger
        from backend.observability.graph import TraceGraphBuilder

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}

        events = ledger.get_trace(trace_id)
        builder = TraceGraphBuilder()
        graph = builder.build(trace_id, events)

        if not graph:
            raise HTTPException(status_code=404, detail="Trace not found or empty")

        return graph
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get trace graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/events")
async def query_events(
    trace_id: Optional[str] = None,
    session_id: Optional[str] = None,
    adr_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
):
    """Query events with filters"""
    try:
        from backend.observability import get_ledger
        from backend.observability.events import EventType

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}

        evt_type = EventType(event_type) if event_type else None
        events = ledger.query_events(
            trace_id=trace_id,
            session_id=session_id,
            adr_id=adr_id,
            event_type=evt_type,
            limit=limit,
        )
        return {"events": [e.to_dict() for e in events], "count": len(events)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get trace graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 🔀 CHANNEL COORDINATION (Phase 2)
# =============================================================================


@app.get("/channels")
async def list_active_channels():
    """List all active communication channels"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}

        channels = router.get_active_channels()
        return {"channels": [c.to_dict() for c in channels], "count": len(channels)}
    except Exception as e:
        logger.error(f"List channels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/channels/{channel_id}/terminate")
async def terminate_channel(channel_id: str, reason: str = "User requested"):
    """Emergency channel termination (human override)"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}

        result = await router.terminate_channel(
            channel_id=channel_id, reason=reason, terminated_by="human"
        )
        return result
    except Exception as e:
        logger.error(f"Terminate channel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/channels/stats")
async def get_channel_stats():
    """Get channel router statistics"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}

        return router.get_stats()
    except Exception as e:
        logger.error(f"Channel stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/channels/{channel_id}")
async def get_channel_details(channel_id: str):
    """Get detailed information about a specific channel"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}

        channel = router.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        return channel.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get channel error: {e}")


# New: /api/status endpoint (alias)
@app.get("/api/status")
async def get_api_status():
    return await get_status()


# Duplicate channel endpoints removed here; original definitions above are used.
# This avoids FastAPI route redeclaration errors.


# =============================================================================
# 📋 CONDITIONAL POLICY MANAGEMENT (Phase 3 Advanced)
# =============================================================================


@app.get("/policies")
async def list_policies():
    """List all available policies (static and conditional)"""
    try:
        from backend.coordination.advanced_policies import get_policy_registry

        registry = get_policy_registry()
        policies = registry.list_all()

        return {
            "policies": [
                {
                    "name": p.name,
                    "description": p.description,
                    "type": "conditional" if hasattr(p, "conditions") else "static",
                    "allowed_actions": [a.value for a in p.allowed_actions],
                    "max_messages": p.max_messages,
                    "max_duration_seconds": p.max_duration_seconds,
                    "requires_human_approval": p.requires_human_approval,
                    "conditions_count": len(p.conditions)
                    if hasattr(p, "conditions")
                    else 0,
                }
                for p in policies
            ],
            "count": len(policies),
        }
    except Exception as e:
        logger.error(f"List policies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policies/{policy_name}")
async def get_policy_details(policy_name: str):
    """Get detailed policy information"""
    try:
        from backend.coordination.advanced_policies import get_policy_registry

        registry = get_policy_registry()
        policy = registry.get(policy_name)

        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        details = {
            "name": policy.name,
            "description": policy.description,
            "type": "conditional" if hasattr(policy, "conditions") else "static",
            "allowed_actions": [a.value for a in policy.allowed_actions],
            "max_messages": policy.max_messages,
            "max_duration_seconds": policy.max_duration_seconds,
            "requires_human_approval": policy.requires_human_approval,
            "alert_on_violations": policy.alert_on_violations,
        }

        # Add conditional policy details
        if hasattr(policy, "conditions"):
            details["conditions"] = [c.to_dict() for c in policy.conditions]
            details["fallback_policy"] = (
                policy.fallback_policy.name if policy.fallback_policy else None
            )
            details["evaluation_strategy"] = policy.evaluation_strategy

        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get policy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policies/test/{policy_name}")
async def test_policy_evaluation(policy_name: str, context: dict):
    """
    Test conditional policy evaluation with given context.

    Request body:
    {
        "from_agent": "agent_id",
        "to_agent": "other_agent_id"
    }

    Returns which policy would be active given current conditions.
    """
    try:
        from backend.coordination.advanced_policies import (
            ConditionalPolicy,
            get_policy_registry,
        )

        registry = get_policy_registry()
        policy = registry.get(policy_name)

        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        if not isinstance(policy, ConditionalPolicy):
            return {
                "policy_name": policy.name,
                "type": "static",
                "message": "Policy is static, no evaluation needed",
            }

        # Build context for evaluation
        router = get_channel_router()
        from_agent = context.get("from_agent", "test_agent")
        to_agent = context.get("to_agent", "target_agent")

        eval_context = await router._build_policy_context(from_agent, to_agent)

        # Evaluate
        active_policy = policy.evaluate(eval_context)

        # Check which conditions passed
        condition_results = [
            {
                "condition": getattr(c, "to_dict", lambda: {})(),
                "passed": bool(getattr(c, "evaluate", lambda ctx: True)(eval_context)),
                "actual_value": eval_context.get(getattr(c, "type", "unknown")),
            }
            for c in getattr(policy, "conditions", [])
        ]

        # Normalize evaluate() result: some implementations return bool, others may return an active policy
        if isinstance(active_policy, bool):
            evaluated_to = policy.name if active_policy else "DENIED"
            used_fallback = False
        else:
            evaluated_to = getattr(active_policy, "name", str(active_policy))
            used_fallback = evaluated_to != getattr(policy, "name", "")

        return {
            "policy_name": getattr(policy, "name", "unknown"),
            "type": "conditional",
            "context": eval_context,
            "evaluated_to": evaluated_to,
            "conditions": condition_results,
            "used_fallback": used_fallback,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test policy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 📡 SCP WEBSOCKET & PATTERN DETECTION (Phase 3)
# =============================================================================


@app.websocket("/ws/scp")
async def scp_websocket(websocket: WebSocket):
    """Real-time event streaming for SCP dashboard"""
    from backend.observability.broadcaster import get_broadcaster

    await websocket.accept()
    broadcaster = get_broadcaster()
    broadcaster.subscribe(websocket)

    try:
        # Keep connection alive and handle client messages
        while True:
            data = await websocket.receive_text()
            # Handle control commands from SCP
            import json

            try:
                command = json.loads(data)
                if command.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except Exception as e:
        logger.error(f"SCP WebSocket error: {e}")
    finally:
        broadcaster.unsubscribe(websocket)


# Minimal safe stub for terminal WebSocket to prevent frontend errors.
@app.websocket("/api/ws/terminal")
async def websocket_terminal_stub(websocket: WebSocket):
    """
    Stubbed terminal WebSocket. Accepts connection and keeps it open, echoing a friendly notice.
    Prevents frontend from failing when the real terminal service is unavailable.
    """
    await websocket.accept()
    await websocket.send_text(
        "Terminal service is not implemented in this demo. Commands will be ignored.\r\n"
    )
    try:
        while True:
            # Consume incoming messages to keep the socket healthy.
            await websocket.receive_text()
            await websocket.send_text("\r\n[stub] command ignored\r\n")
    except WebSocketDisconnect:
        # Client closed; nothing to do.
        pass


@app.get("/patterns/alerts")
async def get_pattern_alerts(limit: int = 10):
    """Get recent pattern detection alerts"""
    try:
        from backend.observability import get_ledger
        from backend.observability.patterns import get_detector

        detector = get_detector()
        alerts = detector.get_recent_alerts(limit=limit)
        serialized = [
            {
                "alert_id": getattr(a, "alert_id", f"alert-{i}"),
                "severity": getattr(a, "severity", "info"),
                "pattern": getattr(a, "pattern", "pattern"),
                "description": getattr(a, "description", ""),
                "timestamp": getattr(a, "timestamp", datetime.utcnow()).isoformat(),
                "event_count": len(getattr(a, "events", [])),
            }
            for i, a in enumerate(alerts)
        ]
        # Fallback: إذا لا توجد تنبيهات، نبني تنبيهًا مبسطًا للإشارة إلى حالة النظام
        if not serialized:
            try:
                ledger = get_ledger()
                events = ledger.query_events(limit=10) if ledger else []
                serialized.append(
                    {
                        "alert_id": "fallback-1",
                        "severity": "info",
                        "pattern": "Observability Feed",
                        "description": f"{len(events)} events observed in ledger.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "event_count": len(events),
                    }
                )
            except Exception as fallback_err:
                logger.warning(f"Pattern alerts fallback error: {fallback_err}")
        return {"alerts": serialized, "count": len(serialized)}
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/patterns/detect")
async def run_pattern_detection(window_minutes: int = 5):
    """Run pattern detection on recent events"""
    try:
        from datetime import datetime, timedelta

        from backend.observability import get_ledger
        from backend.observability.patterns import get_detector

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}

        # Get recent events
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        all_events = ledger.query_events(limit=1000)
        recent = [e for e in all_events if e.timestamp >= cutoff]

        # Detect patterns
        detector = get_detector()
        alerts = detector.detect_patterns(recent, window_minutes=window_minutes)

        return {
            "analyzed_events": len(recent),
            "alerts_found": len(alerts),
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "pattern": a.pattern,
                    "description": a.description,
                }
                for a in alerts
            ],
        }
    except Exception as e:
        logger.error(f"Pattern detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 🧠 ML-BASED ANOMALY DETECTION (Phase 3 Advanced)
# =============================================================================


@app.get("/ml/status")
async def get_ml_status():
    """Get ML detector status and training info"""
    try:
        from backend.observability.ml_detector import get_ml_detector

        detector = get_ml_detector()

        return {
            "sklearn_available": detector.sklearn_available,
            "trained": detector.trained,
            "training_event_count": detector.training_event_count,
            "last_training_time": detector.last_training_time.isoformat()
            if detector.last_training_time
            else None,
            "hours_since_training": detector.hours_since_training(),
            "total_anomalies_detected": len(detector.detected_anomalies),
            "method": "ml"
            if detector.sklearn_available and detector.trained
            else "rule-based",
        }
    except Exception as e:
        logger.error(f"ML status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ml/train")
async def train_ml_models():
    """Manually trigger ML model training"""
    try:
        from backend.observability import get_ledger
        from backend.observability.ml_detector import get_ml_detector

        ledger = get_ledger()

        if not ledger:
            raise HTTPException(status_code=503, detail="Observability not initialized")

        detector = get_ml_detector()

        if not detector.sklearn_available:
            return {
                "error": "scikit-learn not available",
                "install": "pip install scikit-learn numpy",
            }

        # Get historical events
        events = ledger.query_events(limit=5000)

        if len(events) < 100:
            return {
                "error": "Insufficient training data",
                "required": 100,
                "current": len(events),
            }

        # Train models
        result = detector.train(events)

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/anomalies")
async def get_ml_anomalies(window_minutes: int = 15, limit: int = 20):
    """Get ML-detected anomalies"""
    try:
        from datetime import timedelta

        from backend.observability import get_ledger
        from backend.observability.ml_detector import get_ml_detector

        ledger = get_ledger()
        if not ledger:
            raise HTTPException(status_code=503, detail="Observability not initialized")

        detector = get_ml_detector()

        # Get recent events
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        all_events = ledger.query_events(limit=1000)
        recent = [e for e in all_events if e.timestamp >= cutoff]

        # Detect anomalies
        anomalies = detector.detect_anomalies(recent)

        return {
            "anomalies": [a.to_dict() for a in anomalies],
            "count": len(anomalies),
            "analyzed_events": len(recent),
            "window_minutes": window_minutes,
            "method": "ml"
            if detector.sklearn_available and detector.trained
            else "rule-based",
            "trained": detector.trained,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML anomalies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/anomalies/history")
async def get_anomaly_history(limit: int = 50):
    """Get historical anomalies"""
    try:
        from backend.observability.ml_detector import get_ml_detector

        detector = get_ml_detector()
        anomalies = detector.get_recent_anomalies(limit=limit)

        return {
            "anomalies": [a.to_dict() for a in anomalies],
            "count": len(anomalies),
            "total_detected": len(detector.detected_anomalies),
        }
    except Exception as e:
        logger.error(f"Anomaly history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 🧠 EXTENDED MIND (Graph Visualization)
# =============================================================================


@app.get("/mind/graph")
async def get_mind_graph():
    """Get the node-link data for the Extended Mind visualization"""
    try:
        import sqlite3

        db_path = BASE_DIR / "data" / "extended_mind.db"

        if not db_path.exists():
            # Return empty graph if DB doesn't exist yet
            return {"nodes": [], "links": []}

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch Nodes
        cursor.execute("SELECT id, label, type, color, val FROM nodes")
        nodes_rows = cursor.fetchall()
        nodes = [dict(row) for row in nodes_rows]

        # Fetch Edges (Links)
        # Assuming table is 'edges' with source, target
        cursor.execute("SELECT source, target, label FROM edges")
        edges_rows = cursor.fetchall()
        links = [dict(row) for row in edges_rows]

        conn.close()

        return {"nodes": nodes, "links": links}

    except Exception as e:
        logger.error(f"Graph API Error: {e}")
        # Return fallback data for now so UI doesn't crash
        return {
            "nodes": [
                {"id": "root", "label": "Extended Mind", "color": "#4f46e5", "val": 10},
                {"id": "concept-1", "label": "Authority", "color": "#ef4444", "val": 5},
                {"id": "policy-1", "label": "P-ARCH-04", "color": "#f59e0b", "val": 5},
            ],
            "links": [
                {"source": "root", "target": "concept-1"},
                {"source": "root", "target": "policy-1"},
            ],
        }


# Alias under /api for frontend convenience
@app.get("/api/mind/graph")
async def get_mind_graph_api():
    return await get_mind_graph()


# =============================================================================
# 📂 KNOWLEDGE BASE & DOCS MANAGEMENT
# =============================================================================


@app.get("/system/docs/tree")
async def get_docs_tree():
    """Get file structure of the knowledge base"""
    try:
        kb_path = BASE_DIR / "data" / "kb"
        # Ensure directory exists
        kb_path.mkdir(parents=True, exist_ok=True)

        def build_tree(path: Path) -> List[Dict]:
            tree = []
            try:
                # Sort: directories first, then files
                items = sorted(
                    path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
                )
                for item in items:
                    if item.name.startswith("."):
                        continue

                    node = {
                        "name": item.name,
                        "path": str(item.relative_to(BASE_DIR)).replace("\\", "/"),
                        "type": "folder" if item.is_dir() else "file",
                    }
                    if item.is_dir():
                        node["children"] = build_tree(item)
                    tree.append(node)
            except Exception as e:
                logger.error(f"Error scanning {path}: {e}")
            return tree

        return {"roots": build_tree(kb_path)}
    except Exception as e:
        logger.error(f"Docs tree error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias under /api for frontend convenience
@app.get("/api/system/docs/tree")
async def get_docs_tree_api():
    return await get_docs_tree()


@app.get("/system/docs/content")
async def get_doc_content(path: str):
    """Read content of a file"""
    try:
        # Security check: Ensure path is within BASE_DIR
        target_path = (BASE_DIR / path).resolve()
        if not str(target_path).startswith(str(BASE_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")

        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if target_path.suffix.lower() not in [
            ".md",
            ".txt",
            ".json",
            ".yaml",
            ".yml",
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".css",
            ".html",
        ]:
            return {
                "path": path,
                "content": "Binary or unsupported file type",
                "mime": "application/octet-stream",
            }

        content = target_path.read_text(encoding="utf-8")
        return {"path": path, "content": content, "mime": "text/plain"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Read doc error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias under /api for frontend convenience
@app.get("/api/system/docs/content")
async def get_doc_content_api(path: str):
    return await get_doc_content(path)


@app.post("/system/docs/save")
async def save_doc_content(payload: Dict[str, str]):
    """Save content to a file"""
    try:
        path = payload.get("path")
        content = payload.get("content")

        if not path or content is None:
            raise HTTPException(status_code=400, detail="Missing path or content")

        # Security check
        target_path = (BASE_DIR / path).resolve()
        if not str(target_path).startswith(str(BASE_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")

        # Allow writing
        target_path.write_text(content, encoding="utf-8")
        return {"status": "success", "path": path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save doc error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias under /api for frontend convenience
@app.post("/api/system/docs/save")
async def save_doc_content_api(payload: Dict[str, str]):
    return await save_doc_content(payload)


@app.get("/api/workspace")
async def list_workspace(path: str = ".", limit: int = 200):
    """List files in the AI workspace (data/ai_workspace) with safety checks."""
    try:
        target = (workspace_base / path).resolve()
        if not str(target).startswith(str(workspace_base)):
            raise HTTPException(status_code=403, detail="Access denied")
        if not target.exists():
            return {"files": [], "status": "not_found"}
        entries = []
        for entry in target.iterdir():
            if len(entries) >= limit:
                break
            entries.append(
                {
                    "path": str(entry.relative_to(workspace_base)).replace("\\", "/"),
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else 0,
                    "modified": datetime.fromtimestamp(
                        entry.stat().st_mtime
                    ).isoformat(),
                }
            )
        return {"files": entries, "status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workspace list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workspace/read")
async def read_workspace_file(path: str):
    """Read a text file from the AI workspace."""
    try:
        target = (workspace_base / path).resolve()
        if not str(target).startswith(str(workspace_base)):
            raise HTTPException(status_code=403, detail="Access denied")
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        # Limit read size for safety
        content = target.read_text(encoding="utf-8", errors="ignore")
        return {"path": path, "content": content, "size": len(content)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workspace read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 💬 COC CONVERSATIONAL CHAT (Phase 3)
# =============================================================================


@app.post("/coc/chat")
async def conversational_chat(
    message: str, session_id: Optional[str] = None, user_id: str = "default_user"
):
    """
    Main COC endpoint - Natural language conversation.

    Flow:
    1. Get or create session
    2. Add user message to history
    3. Use dialogue manager to determine next action
    4. Resolve intent with context
    5. Execute or clarify as needed
    6. Generate natural response
    7. Update session state
    """
    try:
        from datetime import datetime

        from backend.conversation.composer import ResponseComposer
        from backend.conversation.dialogue_manager import get_dialogue_manager
        from backend.conversation.intent_resolver import IntentResolver
        from backend.conversation.orchestrator import ConversationOrchestrator
        from backend.conversation.session import get_session_manager
        from backend.observability import get_ledger
        from backend.observability.events import EventType

        # Get managers
        session_mgr = get_session_manager()
        dialogue_mgr = get_dialogue_manager()

        ledger = get_ledger()

        # Get or create session
        if session_id:
            session = session_mgr.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = session_mgr.create_session(user_id)

        # Log COC message event
        if ledger:
            _log_fn = getattr(ledger, "log", None)
            if callable(_log_fn):
                _log_fn(
                    EventType.USER_MESSAGE,
                    user_id,
                    "coc_chat",
                    input_payload={
                        "message": message,
                        "session_id": session.session_id,
                    },
                )

        # Add user message to history
        session_mgr.add_message(session.session_id, "user", message)

        # Determine next action using dialogue manager
        next_action = dialogue_mgr.get_next_action(session, message)

        # Handle greeting
        if next_action["action"] == "greet":
            dialogue_mgr.update_state(
                session, next_action["dialogue_state"], "greeting"
            )
            response_text = (
                "Hello! I'm ICGL, your Intentional Code Governance Layer assistant. "
                "I can help you with:\n"
                "• Creating collaboration channels between agents\n"
                "• Binding and managing governance policies\n"
                "• Analyzing your codebase\n"
                "• Querying the knowledge base\n\n"
                "What would you like to do?"
            )

            session_mgr.add_message(session.session_id, "assistant", response_text)
            session_mgr.update_session(session)

            return {
                "session_id": session.session_id,
                "response": response_text,
                "dialogue_state": next_action["dialogue_state"].value,
                "needs_clarification": False,
                "pending_approval": None,
            }

        # Resolve intent with context
        resolver = IntentResolver()
        context_summary = dialogue_mgr.summarize_context(session.context)

        # Inject context into message for better resolution
        contextual_message = (
            f"{context_summary}\n\nCurrent message: {message}"
            if context_summary
            else message
        )
        intent_result = resolver.resolve(contextual_message)

        # Update last intent
        if hasattr(intent_result, "intent_type"):
            session.context.last_intent = intent_result.intent_type
        elif isinstance(intent_result, str):
            session.context.last_intent = intent_result

        # Check if clarification needed
        if dialogue_mgr.should_clarify(intent_result, session.context):
            dialogue_mgr.update_state(
                session, next_action["dialogue_state"], "needs_clarification"
            )

            # Generate clarification question (simplified for now)
            clarification_text = (
                "I need a bit more information to help you with that. "
                "Could you please clarify what you'd like me to do?"
            )

            session.context.clarification_history.append(
                {
                    "question": clarification_text,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            session_mgr.add_message(session.session_id, "assistant", clarification_text)
            session_mgr.update_session(session)

            return {
                "session_id": session.session_id,
                "response": clarification_text,
                "dialogue_state": "clarifying",
                "needs_clarification": True,
                "pending_approval": None,
            }

        # Check if approval needed
        if dialogue_mgr.needs_approval(intent_result):
            dialogue_mgr.update_state(
                session, next_action["dialogue_state"], "requesting_approval"
            )

            approval_text = (
                "This action requires your explicit approval because it has high risk. "
                "Would you like me to proceed?"
            )

            session_mgr.add_message(session.session_id, "assistant", approval_text)
            session_mgr.update_session(session)

            return {
                "session_id": session.session_id,
                "response": approval_text,
                "dialogue_state": "confirming",
                "needs_clarification": False,
                "pending_approval": {
                    "intent": str(intent_result),
                    "risk_level": "high",
                },
            }

        # Execute through orchestrator
        dialogue_mgr.update_state(session, next_action["dialogue_state"], "executing")

        orchestrator = ConversationOrchestrator()
        result = await orchestrator.handle(intent_result, {})

        # Generate response
        composer = ResponseComposer()
        response_text = composer.compose(intent_result, result)

        # Update to reporting state
        dialogue_mgr.update_state(
            session, next_action["dialogue_state"], "reporting_result"
        )

        session_mgr.add_message(session.session_id, "assistant", response_text)
        session_mgr.update_session(session)

        return {
            "session_id": session.session_id,
            "response": response_text,
            "dialogue_state": "reporting",
            "needs_clarification": False,
            "pending_approval": None,
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"COC chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 💬 COC SESSION MANAGEMENT (Phase 1)
# =============================================================================


@app.post("/coc/sessions")
async def create_conversation_session(user_id: str):
    """Create new conversation session"""
    try:
        from backend.conversation.session import get_session_manager

        manager = get_session_manager()
        session = manager.create_session(user_id)

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "status": session.status.value,
        }
    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coc/sessions/{session_id}")
async def get_conversation_session(session_id: str):
    """Get session details"""
    try:
        from backend.conversation.session import get_session_manager

        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coc/sessions/{session_id}/history")
async def get_conversation_history(session_id: str, limit: int = 50):
    """Get conversation history"""
    try:
        from backend.conversation.session import get_session_manager

        manager = get_session_manager()
        messages = manager.get_conversation_history(session_id, limit=limit)

        return {
            "session_id": session_id,
            "messages": [m.to_dict() for m in messages],
            "count": len(messages),
        }
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/coc/sessions/{session_id}")
async def close_conversation_session(session_id: str):
    """Close conversation session"""
    try:
        from backend.conversation.session import get_session_manager

        manager = get_session_manager()
        manager.close_session(session_id)

        return {"status": "closed", "session_id": session_id}
    except Exception as e:
        logger.error(f"Close session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coc/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, status: Optional[str] = None):
    """Get all sessions for a user"""
    try:
        from backend.conversation.session import get_session_manager

        manager = get_session_manager()

        # Try to coerce into SessionStatus if available
        try:
            from backend.conversation.session import SessionStatus

            status_enum = SessionStatus(status) if status else None
        except Exception:
            status_enum = status

        sessions = manager.get_user_sessions(user_id, status=status_enum)

        return {
            "user_id": user_id,
            "sessions": [s.to_dict() for s in sessions],
            "count": len(sessions),
        }
    except Exception as e:
        logger.error(f"Get user sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 🚀 SERVER ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys

    import uvicorn

    port = 5173
    # السماح بتمرير المنفذ من سطر الأوامر أو متغير بيئة
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception:
            pass
    port = int(os.getenv("API_PORT", port))
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, reload=True)
    except Exception:
        import traceback

        print("\n\n❌ Exception during server startup:")
        print(traceback.format_exc())
