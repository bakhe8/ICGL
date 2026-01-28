from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Router imports
# Router imports
from src.api.routers import agents, chat, executive, governance, ops, system

# src imports
from src.core.utils.logging_config import get_logger

# 1. 🔴 MANDATORY: Load Environment FIRST
BASE_DIR = Path(__file__).parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

logger = get_logger(__name__)

# Initialize FastAPI
app = FastAPI(title="ICGL Sovereign Cockpit API", version="1.3.0")
root_app = FastAPI(title="ICGL Root")

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


# --- Router Integration (Unified API v1 & Direct) ---
# We use prefixes that match the frontend queries.ts expectations
app.include_router(governance.router, prefix="/governance", tags=["Governance"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(system.router, prefix="/system", tags=["System"])
app.include_router(chat.router, prefix="/chat", tags=["Collaboration"])
app.include_router(executive.router, prefix="/executive", tags=["Human Bridge"])
app.include_router(ops.router, prefix="/ops", tags=["Operations"])

# Legacy/V1 Aliases (Optional but recommended)
app.include_router(governance.router, prefix="/v1/adr", tags=["Legacy"])
app.include_router(system.router, prefix="/v1/system", tags=["Legacy"])

# Mount API to root
root_app.mount("/api", app)
