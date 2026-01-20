from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from contextlib import asynccontextmanager
import httpx
import os
import time
import traceback
from pathlib import Path
from dotenv import load_dotenv

from utils.logging_config import get_logger
from api.routers import system, governance, chat, observability, hr, terminal, scp
from api.dependencies import root_dir

# Initialize Logger
logger = get_logger(__name__)

# Load Environment
load_dotenv(dotenv_path=root_dir / ".env")
start_time_app = time.time()

# --- Dev Proxy Lifecycle ---
proxy_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global proxy_client
    # Startup: Initialize persistent client
    proxy_client = httpx.AsyncClient(timeout=10.0)
    logger.info("🚀 Persistent Dev Proxy Client initialized (Modular)")
    yield
    # Shutdown: Close client
    await proxy_client.aclose()
    logger.info("🛑 Persistent Dev Proxy Client closed")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Sovereign ICGL API",
    version="5.0.0 (Modular)",
    lifespan=lifespan
)

# --- Global Exception Middleware ---
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"❌ Global Exception: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Sovereign System Internal Error",
                "detail": str(e),
                "type": type(e).__name__,
                "suggestion": "Check server logs for detailed stack trace."
            }
        )

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(system.router)
app.include_router(governance.router)
app.include_router(chat.router)
app.include_router(observability.router)
app.include_router(hr.router)
app.include_router(terminal.router)
app.include_router(scp.router)

# --- Static Files & Dashboard ---
ui_path = root_dir / "web" / "dist"
VITE_DEV_PROXY = os.getenv("VITE_DEV_PROXY", "false").lower() == "true"

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/dashboard")

if VITE_DEV_PROXY:
    @app.api_route("/dashboard/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def dashboard_proxy(path: str, request: Request):
        target_url = f"http://localhost:5173/dashboard/{path}"
        logger.info(f"🔀 Proxying to Vite: {target_url}")
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body()
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)

elif ui_path.exists():
    app.mount("/assets", StaticFiles(directory=str(ui_path / "assets")), name="assets")
    
    @app.get("/dashboard/{full_path:path}")
    async def spa_catch_all(full_path: str):
        return FileResponse(str(ui_path / "index.html"))
else:
    logger.warning("⚠️ Dashboard build not found. Run 'npm run build' in web/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
