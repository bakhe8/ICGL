import asyncio

import websockets


async def test_ws(uri):
    print(f"Testing {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Successfully connected to {uri}")
            await websocket.close()
            return True
    except Exception as e:
        print(f"Failed to connect to {uri}: {e}")
        return False


async def main():
    uri_root = "ws://127.0.0.1:8000/ws/chat"
    uri_api = "ws://127.0.0.1:8000/api/ws/chat"

    success_root = await test_ws(uri_root)
    success_api = await test_ws(uri_api)

    if success_root:
        print("PASS: Root /ws/chat is accessible")
    else:
        print("FAIL: Root /ws/chat is NOT accessible")

    if success_api:
        print("PASS: /api/ws/chat is accessible")
    else:
        print("FAIL: /api/ws/chat is NOT accessible")


if __name__ == "__main__":
    asyncio.run(main())
