import asyncio
import httpx
import time
import uvicorn
from threading import Thread
from icgl.api.server import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001)

async def test_api():
    print("🖥️ Starting API Server (Port 8001)...")
    # Start server in background thread for testing
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for startup
    time.sleep(2) 
    
    base_url = "http://127.0.0.1:8001"
    
    async with httpx.AsyncClient() as client:
        # Test /status
        print(f"   📡 Testing GET {base_url}/status...")
        r = await client.get(f"{base_url}/status")
        if r.status_code == 200:
            print(f"      ✅ OK: Mode={r.json().get('mode')}")
        else:
            print(f"      ❌ FAILED: {r.status_code} {r.text}")
            
        # Test /metrics
        print(f"   📡 Testing GET {base_url}/metrics...")
        r = await client.get(f"{base_url}/metrics")
        if r.status_code == 200:
            print(f"      ✅ OK: Interventions={r.json().get('intervention_count')}")
        else:
            print(f"      ❌ FAILED: {r.status_code} {r.text}")

        # Test /analyze/latest
        print(f"   📡 Testing GET {base_url}/analyze/latest...")
        r = await client.get(f"{base_url}/analyze/latest")
        if r.status_code == 200:
             print(f"      ✅ OK: Found Run Data.")
        else:
             print(f"      ⚠️ Info: {r.status_code} (Might be 404 if no runs exist yet).")

if __name__ == "__main__":
    try:
        import httpx
        asyncio.run(test_api())
    except ImportError:
        print("❌ 'httpx' not installed. Running 'pip install httpx'...")
        import os
        os.system("pip install httpx")
        # Retry once
        import httpx
        asyncio.run(test_api())
