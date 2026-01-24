import asyncio

import httpx


async def test_executive_loop():
    url = "http://localhost:8000/api/governance/executive/chat"

    payload = {
        "message": "أريد منك إضافة ميزة جديدة للنظام تقوم بتسجيل وقت دخول المستخدم."
    }

    print(f"🚀 Sending request to Executive Agent: {payload['message']}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()

            print("\n--- 🧠 Executive Agent Response ---")
            print(f"Status: {data.get('status')}")
            print(f"Agent ID: {data.get('agent_id')}")
            print(f"Message: {data.get('message')}")
            print(f"Clarity Needed: {data.get('action_required')}")
            print(f"Clarity Question: {data.get('clarity_question')}")
            print("-" * 35)

            if data.get("action_required"):
                print(
                    "\n✅ SUCCESS: The 'Confirmation Mirror' is working. The agent asked for clarification before proceeding."
                )
            else:
                print("\n❌ FAILURE: The agent did not flag for clarification.")

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Note: Ensure the local server is running on port 8000.")


if __name__ == "__main__":
    asyncio.run(test_executive_loop())
