import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "sentinel",
    "problem_title": "SOVEREIGN SYSTEM AUDIT (PHASE 9)",
    "problem_context": """
    Perform a comprehensive audit of the ICGL system state after Phase 1-8 upgrades.
    
    Current Components Available:
    - Institutional Memory (Steward)
    - DevOps & CI Monitoring (DevOps)
    - Aesthetic Sovereignty & UI Topology (UI/UX)
    - Self-Expansion Protocols (BaseAgent)
    - Inter-Agent Consultation (Registry)
    
    Audit Mission:
    1. Assess the maturity of the 'Sovereign Council'. Does the system feel autonomous and complete?
    2. Identify any remaining gaps in 'Consensus Logic' or 'Operational Stability'.
    3. Evaluate if the recent UI upgrades (Phase 7) effectively communicate system state to human stakeholders.
    4. Propose the NEXT level of evolution (Phase 10+).
    """,
}

try:
    print("🌌 Initiating Final Meta-Audit: The Sovereign Awakening...")
    print("-" * 50)
    response = requests.post(url, json=payload, timeout=300)
    data = response.json()

    print("\n[SENTINEL'S SUPREME ANALYSIS]:")
    print(data.get("analysis", "NO ANALYSIS RECEIVED"))

    print("\n[COUNCIL RECOMMENDATIONS]:")
    for rec in data.get("recommendations", []):
        print(f"  - {rec}")

except Exception as e:
    print(f"FAILED: {e}")
