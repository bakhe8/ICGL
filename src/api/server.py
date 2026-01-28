from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# src imports
# Router imports
# Router imports
from src.api.routers import adr, agents, chat, executive, governance, ops, system
from src.api.schemas import GenericDataResp
from src.core.utils.logging_config import get_logger

# 1. 🔴 MANDATORY: Load Environment FIRST
BASE_DIR = Path(__file__).parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

logger = get_logger(__name__)

# Initialize FastAPI
root_app = FastAPI(title="ICGL Root", version="1.3.0")

root_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dashboard / App Mounting ---
candidate_paths = [
    BASE_DIR / "src" / "ui" / "web-app" / "dist",
]
ui_path = next((p for p in candidate_paths if p.exists()), None)

if ui_path:
    root_app.mount("/app", StaticFiles(directory=str(ui_path), html=True), name="ui_app")
    root_app.mount("/dashboard", StaticFiles(directory=str(ui_path), html=True), name="ui_dashboard")
    logger.info(f"✅ UI loaded from {ui_path}")
else:
    logger.warning("⚠️ UI path not found.")


@root_app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/app/")


@root_app.get("/health", response_model=GenericDataResp)
@root_app.get("/api/health", response_model=GenericDataResp)
@root_app.get("/api/system/health", response_model=GenericDataResp)
async def health_check():
    return GenericDataResp(data={"status": "ok"})


@root_app.get("/status", response_model=GenericDataResp)
@root_app.get("/api/status", response_model=GenericDataResp)
@root_app.get("/api/system/status", response_model=GenericDataResp)
async def get_status_alias() -> GenericDataResp:
    """Consolidated status endpoint for both prefixed and unprefixed calls."""
    from src.api.routers.system import get_system_status

    return await get_system_status()


@root_app.get("/api/events")
async def get_system_events_alias(limit: int = 50):
    """Alias for secretary-logs expected by some frontend components."""
    from src.api.routers.system import secretary_logs

    res = await secretary_logs(limit=limit)
    return {"logs": res.logs, "status": res.status}


@root_app.post("/chat", response_model=GenericDataResp)
@root_app.post("/api/chat", response_model=GenericDataResp)
async def chat_alias(request: dict):
    """Alias for chat endpoint allowing unprefixed calls."""
    from src.api.routers.chat import chat_endpoint
    from src.core.chat.schemas import ChatRequest

    return await chat_endpoint(ChatRequest(**request))


# --- Router Integration (Unified API v1 & Direct) ---
# We use prefixes that match the frontend queries.ts expectations
root_app.include_router(governance.router, prefix="/api/governance", tags=["Governance"])
root_app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
root_app.include_router(system.router, prefix="/api/system", tags=["System"])
root_app.include_router(chat.router, prefix="/api/chat", tags=["Collaboration"])
root_app.include_router(executive.router, prefix="/api/executive", tags=["Human Bridge"])
root_app.include_router(ops.router, prefix="/api/ops", tags=["Operations"])
root_app.include_router(adr.router, prefix="/api/analysis", tags=["Analysis"])
root_app.include_router(adr.router, prefix="/api/idea-summary", tags=["Analysis"])

# Direct access for unprefixed frontend calls (mapped to prefixed routers)
root_app.include_router(ops.router, prefix="/observability", tags=["Observability"])
root_app.include_router(ops.router, prefix="/patterns", tags=["Observability"])
root_app.include_router(governance.router, prefix="/policies", tags=["Governance"])
root_app.include_router(system.router, prefix="/api/workspace", tags=["Workspace"])

# WebSocket Aliases (Matching Vite Proxy)
root_app.add_websocket_route("/ws/chat", chat.websocket_endpoint)
root_app.add_websocket_route("/ws/system/live", system.websocket_endpoint)

# Legacy/V1 Aliases (Optional but recommended)
root_app.include_router(governance.router, prefix="/api/v1/adr", tags=["Legacy"])
root_app.include_router(system.router, prefix="/api/v1/system", tags=["Legacy"])
root_app.include_router(adr.router, prefix="/api/v1/analysis", tags=["Legacy"])
