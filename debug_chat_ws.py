import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://127.0.0.1:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        # 1. Initial Handshake
        init_state = await websocket.recv()
        print(f"Received State: {init_state}")
        
        init_stream = await websocket.recv()
        print(f"Received Stream: {init_stream}")
        
        # 2. Send Message
        msg = {"type": "message", "content": "Hello System"}
        await websocket.send(json.dumps(msg))
        print(f"Sent: {msg}")
        
        # 3. Receive Response (Stream "...", then content)
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"Received: {data}")
                if data.get("type") == "stream" and "System Active" in data.get("content", ""):
                    # Just an example check, break if we get a real response
                    pass
                if data.get("type") == "error":
                    print("Error received")
                    break
            except asyncio.TimeoutError:
                print("Timeout waiting for more tokens")
                break

if __name__ == "__main__":
    asyncio.run(test_chat())
