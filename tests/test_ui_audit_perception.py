import time

import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "ui_ux",
    "problem_title": "Interface Transparency Audit",
    "problem_context": "The CockpitPage seems to lack a clear 'Self-Correction' visualization. We need a component that shows when the system identifies a bug in its own design. Can you identify where this fits in our current topology and request the necessary changes?",
}

try:
    print("🚀 Triggering UI/UX Audit (Designer-Builder Loop)...")
    response = requests.post(url, json=payload, timeout=90)
    data = response.json()

    print("\nAGENT ANALYSIS:")
    print("-" * 50)
    print(data.get("analysis", "NO ANALYSIS FOUND"))

    print("\n🔍 Checking Logs for 'Design Mandate' to Builder...")
    time.sleep(2)
    # Checking if the agent issued a peer consultation
    # (In this simulation, we check the stdout of the server or secretary logs if applicable)

except Exception as e:
    print(f"FAILED: {e}")
