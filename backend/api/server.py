import asyncio
import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.api.schemas import OperationResult

# --- IMPORTS FROM SHARED (BYPASSING BROKEN BACKEND) ---
from shared.python.core.runtime_guard import RuntimeIntegrityGuard
from shared.python.governance.icgl import ICGL
from shared.python.kb.schemas import ADR, uid
from shared.python.utils.logging_config import get_logger

# 1. 🔴 MANDATORY: Load Environment FIRST (Root Cause Fix for OpenAI Key)
# We find the .env relative to this file's root
# backend/api/server.py -> parent=api, parent=backend, parent=root (3 parents)
BASE_DIR = Path(__file__).parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize logger
logger = get_logger(__name__)

if not os.getenv("OPENAI_API_KEY"):
    logger.warning("❌ OPENAI_API_KEY NOT FOUND IN ENVIRONMENT!")

# Initialize FastAPI
app = FastAPI(title="ICGL Sovereign Cockpit API", version="1.2.0")

# Root app that will expose the UI at `/` and mount the API at `/api`.
# We keep the existing `app` as the API application and expose a top-level
# `app` (reassigned later) so uvicorn can run the root application.
root_app = FastAPI(title="ICGL Root")

# Allow CORS on the root app (wraps mounted API as well)
root_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Engine Singleton ---
# Initialized lazily with thread-safe double-checked locking
_icgl_instance: Optional[ICGL] = None
_icgl_lock = threading.Lock()


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
                    from shared.python.observability import init_observability

                    obs_db_path = BASE_DIR / "data" / "observability.db"
                    init_observability(str(obs_db_path))
                    logger.info("📊 Observability Ledger Initialized")

                    # Runtime integrity check
                    rig = RuntimeIntegrityGuard()
                    rig.check()

                    # Boot ICGL
                    _icgl_instance = ICGL(db_path=str(BASE_DIR / "data" / "kb.db"))
                    logger.info("✅ Engine Booted Successfully.")
                except Exception as e:
                    logger.critical(f"❌ Engine Boot Failed: {e}", exc_info=True)
                    raise RuntimeError(f"Engine Failure: {e}")
    return _icgl_instance


# --- Dashboard / App Mounting ---
# Prefer the frontend build in `frontend/web-app/dist` (monorepo layout).
# Also keep the legacy `backend/web/dist` path for backwards compatibility.
candidate_paths = [
    BASE_DIR / "frontend" / "web-app" / "dist",
    Path(__file__).parent.parent / "web" / "dist",
]
ui_path = None
for p in candidate_paths:
    if p.exists():
        ui_path = p
        break

if ui_path:
    # Mount at both /app and /dashboard on the root app so UI is reachable
    # at the top-level paths while the API is mounted under `/api`.
    root_app.mount("/app", StaticFiles(directory=str(ui_path), html=True), name="ui_app")
    root_app.mount("/dashboard", StaticFiles(directory=str(ui_path), html=True), name="ui_dashboard")
    logger.info(f"✅ UI loaded from {ui_path} (mounted at /app and /dashboard)")
else:
    logger.warning(
        f"⚠️ UI path not found. Expected one of: {[str(p) for p in candidate_paths]}. Run frontend build and try again."
    )


# Pragmatic root redirect to the UI entry so requests to `/` land on the SPA.
@root_app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/app/")


# Convenience redirects so the legacy `/docs`, `/redoc` and OpenAPI JSON
# remain reachable at their traditional top-level paths even though the
# API is mounted under `/api`.
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html


@root_app.get("/docs", include_in_schema=False)
async def docs_ui():
    """Serve Swagger UI for the mounted API at `/api` but expose it at `/docs`."""
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="ICGL API Docs")


@root_app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_oauth2_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@root_app.get("/redoc", include_in_schema=False)
async def redoc_ui():
    return get_redoc_html(openapi_url="/api/openapi.json", title="ICGL ReDoc")


@root_app.get("/openapi.json", include_in_schema=False)
async def openapi_schema():
    # Return the OpenAPI schema generated by the mounted API app.
    try:
        schema = app.openapi()
    except Exception:
        # Fallback: call the internal API app's OpenAPI generator if available
        schema = None
    if schema is None:
        raise HTTPException(status_code=500, detail="OpenAPI schema not available")
    return JSONResponse(content=schema)


# Expose the mounted API application's OpenAPI schema explicitly at
# `/api/openapi.json` so the Swagger UI (which points to `/api/openapi.json`)
# reliably sees the API routes even when apps are mounted or wrapped.
@root_app.get("/api/openapi.json", include_in_schema=False)
async def api_openapi_schema():
    try:
        schema = app.openapi()
    except Exception as e:
        logger.warning(f"Could not generate API OpenAPI schema: {e}")
        raise HTTPException(status_code=500, detail="API OpenAPI schema not available")
    return JSONResponse(content=schema)


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


from backend.api.schemas import (
    EventsResp,
    GenericDataResp,
    HealthResp,
    ObservabilityStatsResp,
    TraceDetailsResp,
    TracesResp,
)


@app.get("/health", response_model=HealthResp)
async def health_check() -> HealthResp:
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

    return HealthResp(
        api=status.get("api", "unknown"),
        env_loaded=status.get("env_loaded", False),
        db_lock=status.get("db_lock", None),
        engine_ready=status.get("engine_ready", False),
        db_error=status.get("db_error", None),
    )


@app.get("/status", response_model=GenericDataResp)
async def get_status() -> GenericDataResp:
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

        return GenericDataResp(
            data={
                "mode": "COCKPIT",
                "waiting_for_human": last_adr.status == "DRAFT" if last_adr else False,
                "active_alert_level": alert_level,
                "last_adr_id": last_adr.id if last_adr else None,
                "telemetry": {**global_telemetry, "last_latency_ms": last_latency},
            }
        )
    except Exception as e:
        return {"mode": "ERROR", "error": str(e)}


@app.post("/propose", response_model=OperationResult)
async def propose_decision(req: ProposalRequest, background_tasks: BackgroundTasks) -> OperationResult:
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
        return OperationResult(status="Analysis Triggered", result={"adr_id": adr.id})
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
                if active_synthesis[adr_id].get("status") == "complete" or "synthesis" in active_synthesis[adr_id]:
                    break  # Done
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from analysis/{adr_id}")
    except Exception as e:
        logger.warning(f"Error in analysis stream for {adr_id}: {e}")
        try:
            await websocket.send_json({"error": "Analysis stream error", "message": str(e)})
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
        from shared.python.agents.base import Problem

        # Policy gate check (pre-analysis)
        policy_report = icgl.enforcer.check_adr_compliance(adr)
        if policy_report.status == "FAIL":
            active_synthesis[adr.id] = {"status": "blocked", "policy_report": policy_report.__dict__}
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
        problem = Problem(title=adr.title, context=adr.context, metadata={"decision": adr.decision})

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
                    {"id": a.rule_id, "severity": a.severity.value, "message": a.message, "category": a.category.value}
                    for a in alerts
                ],
                "mindmap": generate_consensus_mindmap(adr.title, synthesis),
                "mediation": None,  # Placeholder
                "policy_report": policy_report.__dict__,
            },
        }

        # 4. Mediation Mode (Phase G) if الثقة منخفضة
        if synthesis.overall_confidence < 0.7:
            logger.info(f"⚖️ Consensus Low ({synthesis.overall_confidence:.2f}). Invoking Mediator...")
            from shared.python.agents.mediator import MediatorAgent

            llm_provider = icgl.registry.get_llm_provider() if hasattr(icgl.registry, "get_llm_provider") else None
            mediator = MediatorAgent(llm_provider=llm_provider)

            problem_mediation = Problem(
                title=adr.title,
                context=adr.context,
                metadata={"decision": adr.decision, "agent_results": [asdict(r) for r in synthesis.individual_results]},
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


@app.get("/analysis/{adr_id}", response_model=GenericDataResp)
async def get_analysis(adr_id: str) -> GenericDataResp:
    if adr_id in active_synthesis:
        return GenericDataResp(data=active_synthesis[adr_id])
    raise HTTPException(status_code=404, detail="Analysis session context lost or not started.")


@app.post("/sign/{adr_id}", response_model=OperationResult)
async def sign_decision(adr_id: str, req: SignRequest) -> OperationResult:
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
            raise HTTPException(status_code=400, detail="Policy gate failed; cannot sign.")
        alerts = result_data["synthesis"].get("sentinel_alerts") or []
        if any(a.get("severity") == "CRITICAL" for a in alerts):
            raise HTTPException(status_code=400, detail="Critical sentinel alert; cannot sign.")

        # Record Decision
        decision = icgl.hdal.sign_decision(adr_id, req.action, req.rationale, req.human_id)

        # Persistence
        adr.status = "ACCEPTED" if req.action == "APPROVE" else "REJECTED"
        adr.human_decision_id = decision.id
        icgl.kb.add_adr(adr)
        icgl.kb.add_human_decision(decision)

        # Execution (Cycle 9)
        if req.action == "APPROVE" and getattr(icgl, "engineer", None):
            all_changes = []
            for res in result_data["synthesis"]["agent_results"]:
                if "file_changes" in res and res["file_changes"]:
                    from shared.python.kb.schemas import FileChange

                    all_changes.extend([FileChange(**fc) for fc in res["file_changes"]])

            if all_changes:
                for change in all_changes:
                    icgl.engineer.write_file(change.path, change.content)
                icgl.engineer.commit_decision(adr, decision)

        return OperationResult(status="Complete", result={"action": req.action})
    except Exception as e:
        logger.error(f"Sign Failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kb/{type}", response_model=GenericDataResp)
async def list_kb(type: str) -> GenericDataResp:
    try:
        icgl = get_icgl()
        if type == "adrs":
            return GenericDataResp(
                data={
                    "adrs": [
                        a.__dict__
                        for a in sorted(list(icgl.kb.adrs.values()), key=lambda x: x.created_at, reverse=True)
                    ]
                }
            )
        if type == "policies":
            return GenericDataResp(data={"policies": [p.__dict__ for p in list(icgl.kb.policies.values())]})
        return GenericDataResp(data={"error": "Invalid KB type"})
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


# =============================================================================
# 💬 CHAT ENDPOINT (Conversational Interface)
# =============================================================================

from shared.python.chat.schemas import ChatRequest, ChatResponse
from shared.python.conversation import ConversationOrchestrator

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
        response = await chat_orchestrator.handle(request)
        # Broadcast to connected chat clients (stateful viewers)
        try:
            await chat_ws_manager.broadcast(jsonable_encoder(response))
        except Exception as e:
            logger.warning(f"Chat broadcast failed: {e}")
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return chat_orchestrator.composer.error(str(e))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await chat_ws_manager.connect(websocket)
    try:
        # send a lightweight ack
        await websocket.send_json({"type": "stream", "content": "Connected via Secure Uplink."})

        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                user_content = data.get("content", "")

                # Create a mock Request object since Orchestrator expects one
                chat_req = ChatRequest(message=user_content)

                # Signal "Thinking" - Let frontend know we are working on it
                await websocket.send_json({"type": "stream", "content": ""})

                logger.info(f"⏳ Processing Chat Request: {user_content[:50]}...")
                start_ts = time.time()

                try:
                    # Process via Orchestrator with timeout safety
                    response = await asyncio.wait_for(chat_orchestrator.handle(chat_req), timeout=25.0)
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
                            await websocket.send_json({"type": "stream", "content": msg.content})

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

            except json.JSONDecodeError:
                pass
            except Exception as e:
                logger.error(f"WS Handling Error: {e}")
                await websocket.send_json({"type": "stream", "content": f"System Error: {str(e)}"})

    except WebSocketDisconnect:
        chat_ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"Chat WS error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
        chat_ws_manager.disconnect(websocket)


@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    """Minimal interactive terminal WebSocket used by the frontend.

    This endpoint echoes received commands and streams simple status
    messages. It's intentionally lightweight and safe.
    """
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "message": "Terminal connected."})
        while True:
            try:
                msg = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            # Echo back as a structured output block
            try:
                await websocket.send_json({"type": "output", "content": f"Received: {msg}"})
            except Exception:
                break
    except WebSocketDisconnect:
        return
    except Exception as e:
        logger.warning(f"Terminal WS error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass


# =============================================================================
# 📊 OBSERVABILITY ENDPOINTS (Phase 1: Read-Only)
# =============================================================================


@app.get("/observability/stats", response_model=ObservabilityStatsResp)
async def get_observability_stats():
    """Get observability ledger statistics"""
    try:
        from shared.python.observability import get_ledger

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        return ObservabilityStatsResp(stats=ledger.get_stats())
    except Exception as e:
        logger.error(f"Observability stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/traces", response_model=TracesResp)
async def list_recent_traces(limit: int = 50):
    """List recent traces with metadata"""
    try:
        from shared.python.observability import get_ledger

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        traces = ledger.get_recent_traces(limit=limit)
        return TracesResp(traces=traces, count=len(traces))
    except Exception as e:
        logger.error(f"List traces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/trace/{trace_id}", response_model=TraceDetailsResp)
async def get_trace_details(trace_id: str):
    """Get complete trace for replay"""
    try:
        from shared.python.observability import get_ledger

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        events = ledger.get_trace(trace_id)
        return TraceDetailsResp(trace_id=trace_id, event_count=len(events), events=[e.to_dict() for e in events])
    except Exception as e:
        logger.error(f"Get trace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/events", response_model=EventsResp)
async def query_events(
    trace_id: Optional[str] = None,
    session_id: Optional[str] = None,
    adr_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
):
    """Query events with filters"""
    try:
        from shared.python.observability import get_ledger
        from shared.python.observability.events import EventType

        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}

        evt_type = EventType(event_type) if event_type else None
        events = ledger.query_events(
            trace_id=trace_id, session_id=session_id, adr_id=adr_id, event_type=evt_type, limit=limit
        )
        return EventsResp(events=[e.to_dict() for e in events], count=len(events))
    except Exception as e:
        logger.error(f"Query events error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pulse/stream", include_in_schema=False)
async def pulse_stream_root(interval: float = 2.0):
    """Server-Sent Events root alias for frontend EventSource('/api/pulse/stream')."""

    async def event_generator():
        try:
            while True:
                from shared.python.observability import get_ledger

                ledger = get_ledger()
                stats = ledger.get_stats() if ledger and hasattr(ledger, "get_stats") else {"status": "no-ledger"}
                payload = {"type": "pulse", "stats": stats}
                yield f"data: {json.dumps(payload, default=str)}\n\n"
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            return

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# =============================================================================
# 🚀 SERVER ENTRY POINT
# =============================================================================

# Also include the API router at the root so endpoints appear both under
# `/api/...` and directly under `/...` for backward compatibility.
# Include additional routers implementing frontend-expected endpoints
try:
    from backend.api.routers import agents as agents_router
    from backend.api.routers import executive as executive_router
    from backend.api.routers import governance as governance_router
    from backend.api.routers import ops as ops_router
    from backend.api.routers import system as system_router

    app.include_router(system_router.router, prefix="/system")
    app.include_router(governance_router.router, prefix="/governance")
    app.include_router(executive_router.router, prefix="/executive")
    app.include_router(agents_router.router, prefix="/agents")
    app.include_router(ops_router.router, prefix="/ops")
    # Also expose these routers under the /api prefix on the root app so
    # the root OpenAPI generator (used by `/docs`) sees them.
    root_app.include_router(system_router.router, prefix="/api/system")
    root_app.include_router(governance_router.router, prefix="/api/governance")
    root_app.include_router(executive_router.router, prefix="/api/executive")
    root_app.include_router(agents_router.router, prefix="/api/agents")
    root_app.include_router(ops_router.router, prefix="/api/ops")
except Exception as e:
    logger.warning(f"Could not include extended routers: {e}")

root_app.include_router(app.router, prefix="")

# Mount the API under /api on the root app and expose `app` as the root ASGI
# application for uvicorn and other runners.
root_app.mount("/api", app)

# Reassign module-level `app` to the root app so callers like
# `uvicorn backend.api.server:app` run the combined application.
app = root_app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
