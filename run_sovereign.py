import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run():
    root_dir = Path(__file__).resolve().parent # ICGL root
    web_dir = root_dir / "web"
    api_dir = root_dir
    
    print("🚀 Starting ICGL Sovereign Monolith...")
    
    # 1. Start Vite Dev Server
    print("📦 Starting Frontend (Vite)...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(web_dir),
        shell=True
    )
    
    # 2. Start Python Backend with Dev Proxy Enabled
    print("🐍 Starting Backend (FastAPI) with Dev Proxy...")
    env = os.environ.copy()
    env["VITE_DEV_PROXY"] = "true"
    
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.server:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=str(api_dir),
        env=env
    )
    
    print("\n✅ System Ready!")
    print("👉 Dashboard: http://localhost:8000")
    print("👉 API Docs:  http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both servers.")
    
    try:
        while True:
            time.sleep(1)
            if frontend_proc.poll() is not None:
                print("❌ Frontend process exited.")
                break
            if backend_proc.poll() is not None:
                print("❌ Backend process exited.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Sovereign Monolith...")
    finally:
        frontend_proc.terminate()
        backend_proc.terminate()
        print("👋 Goodbye.")

if __name__ == "__main__":
    run()
