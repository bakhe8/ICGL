import asyncio
import websockets
import json

async def trigger_live_pulse():
    uri = "ws://127.0.0.1:8000/ws/status"
    print(f"🔌 Connecting to Neural Core at {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Simulate a "Pulse" event that the Dashboard should pick up
            event = {
                "type": "pulse",
                "data": {
                    "source": "CEO_DRILL",
                    "status": "OPERATIONAL",
                    "message": "⚠️ THIS IS A DRILL: Departmental Cohesion Verified.",
                    "timestamp": "2026-01-17T07:30:00Z"
                }
            }
            
            print(f"📡 Broadcasting Event: {event['data']['message']}")
            await websocket.send(json.dumps(event))
            
            # Wait for echo/ack
            response = await websocket.recv()
            print(f"📩 System Response: {response}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("   (Ensure the server is running with 'uvicorn' in another tab)")

if __name__ == "__main__":
    asyncio.run(trigger_live_pulse())
