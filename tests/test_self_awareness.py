import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "architect",
    "problem_title": "Council Capability Audit",
    "problem_context": """
    As the Architect of the Sovereign Council, I want you to perform a gap analysis. 
    Current agents: Architect (Strategy), Builder (Code), Sentinel (Monitoring), Steward (Knowledge), Secretary (Intent), Refactoring (Clean Code), Policy (Compliance), Testing (Safety), DevOps (Environment), UI/UX (Experience).
    
    Mission: Fully autonomous, self-evolving code governance.
    
    Question: Are we missing any specialized roles to achieve Phase 5 (Self-Correction) or complex UI/DevOps automation? 
    If yes, what role would you propose and why?
    """,
}

try:
    response = requests.post(url, json=payload, timeout=90)
    data = response.json()
    print("COUNCIL RESPONSE:")
    print("-" * 50)
    print(data.get("analysis", "NO ANALYSIS FOUND"))
    print("-" * 50)
    print("PROPOSED ROLES/RECOMMENDATIONS:")
    for rec in data.get("recommendations", []):
        print(f"  - {rec}")
except Exception as e:
    print(f"FAILED: {e}")
