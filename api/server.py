import asyncio
import json
import os
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.core.runtime_guard import RuntimeIntegrityGuard
from backend.governance import ICGL

# ICGL Core Imports
from backend.kb import ADR, uid
from backend.utils.logging_config import get_logger

# 1. 🔴 MANDATORY: Load Environment FIRST (Root Cause Fix for OpenAI Key)
# We find the .env relative to this file's root
BASE_DIR = Path(__file__).parent.parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize logger
logger = get_logger(__name__)

if not os.getenv("OPENAI_API_KEY"):
    logger.warning("❌ OPENAI_API_KEY NOT FOUND IN ENVIRONMENT!")

# Initialize FastAPI
app = FastAPI(title="ICGL Sovereign Cockpit API", version="1.2.0")

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
from fastapi.responses import FileResponse

# 1. Static HTML UI Path (for docs/demos)
static_ui_path = Path(__file__).parent.parent / "ui"

# 2. React Basic UI Path (admin tools)
react_basic_path = Path(__file__).parent.parent / "web" / "dist"

# 3. Main React App Path (production UI)
main_app_path = BASE_DIR / "web" / "dist"

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


# Serve landing page as root
@app.get("/")
async def serve_landing():
    """Serve unified landing page as root"""
    landing_path = static_ui_path / "landing.html"
    if landing_path.exists():
        return FileResponse(landing_path)
    # Fallback to main app if landing doesn't exist
    return (
        FileResponse(main_app_path / "index.html")
        if main_app_path.exists()
        else {"error": "No UI found"}
    )


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


# --- Models ---
class ProposalRequest(BaseModel):
    title: str
    context: str
    decision: str
    human_id: str = "bakheet"


class SignRequest(BaseModel):
    action: str
    rationale: str
    human_id: str = "bakheet"


# --- Diagnostic Endpoints ---


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Diagnostic endpoint to verify system sanity."""
    status: Dict[str, Any] = {
        "api": "healthy",
        "env_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "db_lock": "unknown",
        "engine_ready": _icgl_instance is not None,
    }

    try:
        icgl = get_icgl()
        status["engine_ready"] = True
        # Test KB
        icgl.kb.get_adr("test")  # Simple query
        status["db_lock"] = "none"
    except Exception as e:
        status["api"] = "degraded"
        status["db_error"] = str(e)

    return status


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
        return {"status": "Analysis Triggered", "adr_id": adr.id}
    except Exception as e:
        logger.error(f"Proposal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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


async def run_analysis_task(adr: ADR, human_id: str) -> None:
    """Background task to run full ICGL analysis on an ADR."""
    import time

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
        matches = await icgl.memory.search(query, limit=4)
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

        # 3. Agent Synthesis
        problem = Problem(
            title=adr.title, context=adr.context, metadata={"decision": adr.decision}
        )

        synthesis = await icgl.registry.run_and_synthesize(problem, icgl.kb)

        from dataclasses import asdict

        active_synthesis[adr.id] = {
            "adr": asdict(adr),
            "synthesis": {
                "overall_confidence": synthesis.overall_confidence,
                "consensus_recommendations": synthesis.consensus_recommendations,
                "all_concerns": synthesis.all_concerns,
                "agent_results": [asdict(r) for r in synthesis.individual_results],
                "semantic_matches": semantic[:3],
                "sentinel_alerts": [
                    {
                        "id": a.rule_id,
                        "severity": a.severity.value,
                        "message": a.message,
                        "category": a.category.value,
                    }
                    for a in alerts
                ],
                "mindmap": generate_consensus_mindmap(adr.title, synthesis),
                "mediation": None,  # Placeholder
                "policy_report": policy_report.__dict__,
            },
        }

        # 4. Mediation Mode (Phase G) if الثقة منخفضة
        if synthesis.overall_confidence < 0.7:
            logger.info(
                f"⚖️ Consensus Low ({synthesis.overall_confidence:.2f}). Invoking Mediator..."
            )
            from backend.agents.mediator import MediatorAgent

            llm_provider = (
                icgl.registry.get_llm_provider()
                if hasattr(icgl.registry, "get_llm_provider")
                else None
            )
            mediator = MediatorAgent(llm_provider=llm_provider)

            problem_mediation = Problem(
                title=adr.title,
                context=adr.context,
                metadata={
                    "decision": adr.decision,
                    "agent_results": [asdict(r) for r in synthesis.individual_results],
                },
            )
            mediation_result = await mediator.analyze(problem_mediation, icgl.kb)

            active_synthesis[adr.id]["synthesis"]["mediation"] = {
                "analysis": mediation_result.analysis,
                "confidence": mediation_result.confidence,
                "concerns": mediation_result.concerns,
            }
            logger.info("⚖️ Mediation Complete.")

        # FINAL BROADCAST
        await manager.broadcast({"type": "status_update", "status": await get_status()})

        # Update ADR in KB with signals
        adr.sentinel_signals = [str(a) for a in alerts]
        icgl.kb.add_adr(adr)

        duration = round((time.time() - start_time) * 1000)
        active_synthesis[adr.id]["latency_ms"] = duration

        logger.info(f"✨ Analysis Complete for {adr.id} ({duration}ms)")
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
    raise HTTPException(
        status_code=404, detail="Analysis session context lost or not started."
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
        decision = icgl.hdal.sign_decision(
            adr_id, req.action, req.rationale, req.human_id
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
                for change in all_changes:
                    icgl.engineer.write_file(change.path, change.content)
                icgl.engineer.commit_decision(adr, decision)

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
        from ..observability import get_ledger

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
        from ..observability import get_ledger

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
        from ..observability import get_ledger

        ledger = get_ledger()
        if not ledger:
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
        from ..observability import get_ledger
        from ..observability.graph import TraceGraphBuilder

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
        from ..observability import get_ledger
        from ..observability.events import EventType

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


# =============================================================================
# 📋 CONDITIONAL POLICY MANAGEMENT (Phase 3 Advanced)
# =============================================================================


@app.get("/policies")
async def list_policies():
    """List all available policies (static and conditional)"""
    try:
        from ..coordination.advanced_policies import get_policy_registry

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
        from ..coordination.advanced_policies import get_policy_registry

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
        from ..coordination.advanced_policies import (
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
                "condition": c.to_dict(),
                "passed": c.evaluate(eval_context),
                "actual_value": eval_context.get(c.type),
            }
            for c in policy.conditions
        ]

        return {
            "policy_name": policy.name,
            "type": "conditional",
            "context": eval_context,
            "evaluated_to": active_policy.name,
            "conditions": condition_results,
            "used_fallback": active_policy.name != policy.name,
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
    from ..observability.broadcaster import get_broadcaster

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


@app.get("/patterns/alerts")
async def get_pattern_alerts(limit: int = 10):
    """Get recent pattern detection alerts"""
    try:
        from ..observability.patterns import get_detector

        detector = get_detector()
        alerts = detector.get_recent_alerts(limit=limit)
        return {
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "pattern": a.pattern,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat(),
                    "event_count": len(a.events),
                }
                for a in alerts
            ],
            "count": len(alerts),
        }
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/patterns/detect")
async def run_pattern_detection(window_minutes: int = 5):
    """Run pattern detection on recent events"""
    try:
        from datetime import datetime, timedelta

        from ..observability import get_ledger
        from ..observability.patterns import get_detector

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
        from ..observability.ml_detector import get_ml_detector

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

        from ..observability.ml_detector import get_ml_detector

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

        from ..observability.ml_detector import get_ml_detector

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
        from ..observability.ml_detector import get_ml_detector

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

        from ..conversation.composer import ResponseComposer
        from ..conversation.dialogue_manager import get_dialogue_manager
        from ..conversation.intent_resolver import IntentResolver
        from ..conversation.orchestrator import ConversationOrchestrator
        from ..conversation.session import get_session_manager
        from ..observability import get_ledger
        from ..observability.events import EventType

        # Get managers
        session_mgr = get_session_manager()
        dialogue_mgr = get_dialogue_manager()
        from backend.observability import get_ledger

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
            ledger.log(
                EventType.USER_MESSAGE,
                user_id,
                "coc_chat",
                input_payload={"message": message, "session_id": session.session_id},
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
        from ..conversation.session import get_session_manager

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
        from ..conversation.session import get_session_manager

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
        from ..conversation.session import get_session_manager

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
        from ..conversation.session import get_session_manager

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
        from ..conversation.session import SessionStatus, get_session_manager

        manager = get_session_manager()

        status_enum = SessionStatus(status) if status else None
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
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
