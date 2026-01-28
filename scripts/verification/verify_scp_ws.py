import asyncio
import json

import websockets


async def test_scp_ws():
    uri = "ws://127.0.0.1:8000/ws/scp"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")

            # Wait for 3 messages
            for i in range(3):
                msg = await websocket.recv()
                data = json.loads(msg)
                print(f"Received ({i + 1}): {data.get('type')}")
                if data.get("type") == "event":
                    print(f"  Event Type: {data['data'].get('event_type')}")
                    print(f"  Status: {data['data'].get('status')}")

            print("✅ WS Test Passed")
    except Exception as e:
        print(f"❌ WS Test Failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_scp_ws())
