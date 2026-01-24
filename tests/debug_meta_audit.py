import json

import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "guardian_sentinel",
    "problem_title": "SOVEREIGN SYSTEM AUDIT (PHASE 9)",
    "problem_context": "Deep state audit of ICGL components.",
}

try:
    print("🌌 Debugging Final Meta-Audit...")
    response = requests.post(url, json=payload, timeout=300)
    print(f"Status: {response.status_code}")
    print("Raw Response Content:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"FAILED: {e}")
