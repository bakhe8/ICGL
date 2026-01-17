import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://127.0.0.1:8000/ws/chat"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Send message
            msg = {"content": "Bind policy P-ARCH-04 to ADR-001"}
            await websocket.send(json.dumps(msg))
            print(f"Sent: {msg}")
            
            # Receive loop
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                data = json.loads(response)
                print(f"Received: {json.dumps(data, indent=2)}")
                
                if data.get("type") == "stream" and "Confirmation" in data.get("content", ""):
                     print("Received confirmation.")
                     
                if data.get("type") == "block" or (data.get("type") == "stream" and "Analysis ready" in data.get("content", "")):
                    print("Received response. Test passed.")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
