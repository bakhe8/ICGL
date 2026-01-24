import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "refactoring",
    "problem_title": "Synergy Loop Verification",
    "problem_context": "Optimize hdal_agent.py. Consult Builder for impact and Testing for safety.",
}

try:
    response = requests.post(
        url, json=payload, timeout=90
    )  # Large timeout for double consultation
    data = response.json()
    print("ANALYSIS STATUS: SUCCESS")
    print("-" * 50)
    print(data.get("analysis", "NO ANALYSIS FOUND"))
    print("-" * 50)
    print("PEER REFERENCES:")
    refs = data.get("references", [])
    for ref in refs:
        print(f"  - {ref[:200]}...")
except Exception as e:
    print(f"FAILED: {e}")
