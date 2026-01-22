"""
Simple server to link all three ICGL frontend interfaces.
Includes reverse proxy to main backend API.
"""

from pathlib import Path

import asyncio
import httpx
import subprocess
import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ICGL Unified Interface", version="1.0.0")
rebuild_lock = asyncio.Lock()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Paths - Updated for new flat structure
BASE_DIR = Path(__file__).parent.parent  # ICGL root
landing_path = BASE_DIR / "ui" / "landing"
cockpit_path = BASE_DIR / "ui" / "cockpit"
admin_path = BASE_DIR / "admin" / "dist"
web_path = BASE_DIR / "web" / "dist"

print(f"🔍 BASE_DIR: {BASE_DIR}")
print(f"🔍 Landing UI: {landing_path}")
print(f"🔍 Cockpit UI: {cockpit_path}")
print(f"🔍 Admin Tools: {admin_path}")
print(f"🔍 Main App: {web_path}")
print(f"🔗 Backend Proxy: {BACKEND_URL}")

# Mount landing UI
if landing_path.exists():
    app.mount(
        "/ui/landing",
        StaticFiles(directory=str(landing_path), html=True),
        name="landing_ui",
    )
    print(f"✅ Landing UI loaded from {landing_path}")
else:
    print(f"⚠️ Landing UI path not found: {landing_path}")

# Mount cockpit UI
if cockpit_path.exists():
    app.mount(
        "/ui/cockpit",
        StaticFiles(directory=str(cockpit_path), html=True),
        name="cockpit_ui",
    )
    print(f"✅ Cockpit UI loaded from {cockpit_path}")
else:
    print(f"⚠️ Cockpit UI path not found: {cockpit_path}")

# Mount admin tools (SPA Support)
if admin_path.exists():
    # 1. Mount assets specifically
    app.mount(
        "/admin/assets",
        StaticFiles(directory=str(admin_path / "assets")),
        name="admin_assets",
    )

    # 2. Serve Admin SPA fallback
    @app.get("/admin/{path:path}")
    async def serve_admin_spa(path: str):
        # Serve specific root files if they exist (like favicon, etc.)
        file_path = admin_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise fallback to index.html
        return FileResponse(admin_path / "index.html")

    print(f"✅ Admin Tools loaded from {admin_path} (SPA Mode)")
else:
    print(f"⚠️ Admin Tools path not found: {admin_path}")

# Mount main React app (SPA Support)
if web_path.exists():
    # 1. Mount assets specifically
    app.mount(
        "/app/assets",
        StaticFiles(directory=str(web_path / "assets")),
        name="main_app_assets",
    )

    # 2. Serve Main App SPA fallback
    @app.get("/app/{path:path}")
    async def serve_main_spa(path: str):
        # Serve specific root files from dist
        file_path = web_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise fallback to index.html
        return FileResponse(web_path / "index.html")

    print(f"✅ Main App loaded from {web_path} (SPA Mode)")
else:
    print(f"⚠️ Main App path not found: {web_path}")


# Serve landing page as root
@app.get("/")
async def serve_landing():
    """Serve unified landing page"""
    index_file = landing_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "error": "Landing page not found",
        "info": "Check that index.html exists in ui/landing/",
    }


# Serve landing page assets
@app.get("/styles.css")
async def serve_css():
    return FileResponse(landing_path / "styles.css")


@app.get("/script.js")
async def serve_js():
    return FileResponse(landing_path / "script.js")


@app.get("/landing.css")  # Redirect or serve for compatibility
async def serve_legacy_css():
    if (landing_path / "landing.css").exists():
        return FileResponse(landing_path / "landing.css")
    return FileResponse(landing_path / "styles.css")


@app.get("/landing.js")  # Redirect or serve for compatibility
async def serve_legacy_js():
    if (landing_path / "landing.js").exists():
        return FileResponse(landing_path / "landing.js")
    return FileResponse(landing_path / "script.js")


# Health check
@app.get("/health")
async def health():
    """Check health of all interfaces and backend connection"""
    backend_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{BACKEND_URL}/health")
            backend_status = "connected" if response.status_code == 200 else "error"
    except:
        backend_status = "offline"

    return {
        "status": "healthy",
        "interfaces": {
            "landing": (landing_path / "index.html").exists(),
            "cockpit_ui": cockpit_path.exists(),
            "admin_tools": admin_path.exists(),
            "main_app": web_path.exists(),
        },
        "backend": {"url": BACKEND_URL, "status": backend_status},
    }


@app.post("/api/rebuild")
async def rebuild_frontend():
    """
    Trigger frontend rebuild (web/) so new generated files appear.
    """
    if rebuild_lock.locked():
        return {"status": "busy", "message": "Rebuild already running"}

    async with rebuild_lock:
        try:
            loop = asyncio.get_running_loop()

            def run_build():
                import shutil

                npm_path = shutil.which("npm")
                # On Windows, npm is usually npm.cmd
                if not npm_path:
                    npm_path = shutil.which("npm.cmd")
                if not npm_path:
                    return 127, "", "npm not found in PATH"
                proc = subprocess.run(
                    [npm_path, "run", "build"],
                    cwd=str(web_path),
                    capture_output=True,
                    text=True,
                    shell=False,
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


# Reverse Proxy for API endpoints
@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def proxy_to_backend(path: str, request: Request):
    """Proxy requests to main backend if they match /api, /propose, /sign, /status, /kb, etc."""
    # List of paths that should be proxied to backend
    proxy_paths = [
        "api",
        "propose",
        "sign",
        "status",
        "kb",
        "analysis",
        "observability",
        "channels",
        "policies",
        "patterns",
        "ml",
    ]

    # Check if path starts with any proxy path
    should_proxy = any(path.startswith(p) for p in proxy_paths)

    if not should_proxy:
        # Not an API path, return 404
        return {"detail": "Not Found"}

    # Proxy to backend
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{BACKEND_URL}/{path}"
        headers = dict(request.headers)
        headers.pop("host", None)  # Remove host header

        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
                params=request.query_params,
            )

            return StreamingResponse(
                response.iter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.RequestError as e:
            return {"error": "Backend connection failed", "detail": str(e)}


# WebSocket Proxy
@app.websocket("/ws/{path:path}")
async def proxy_websocket(websocket: WebSocket, path: str):
    """Proxy WebSocket to backend"""
    import websockets

    await websocket.accept()
    ws_url = f"ws://127.0.0.1:8000/ws/{path}"

    try:
        async with websockets.connect(ws_url) as backend_ws:
            # Forward messages between client and backend
            async def client_to_backend():
                while True:
                    data = await websocket.receive_text()
                    await backend_ws.send(data)

            async def backend_to_client():
                while True:
                    data = await backend_ws.recv()
                    await websocket.send_text(data)

            import asyncio

            await asyncio.gather(client_to_backend(), backend_to_client())
    except Exception as e:
        print(f"WebSocket proxy error: {e}")
        await websocket.close()


if __name__ == "__main__":
    print("🚀 Starting ICGL Unified Interface Server...")
    print("📍 Routes:")
    print("   /         - Landing Page")
    print("   /ui       - Static HTML UI")
    print("   /admin    - Admin Tools (React Basic)")
    print("   /app      - Main App (React Advanced)")
    print("   /health   - Health Check")
    print(f"   /api/*    - Proxied to {BACKEND_URL}")
    print(f"   /ws/*     - WebSocket proxy to {BACKEND_URL}")
    uvicorn.run(app, host="127.0.0.1", port=8080)
