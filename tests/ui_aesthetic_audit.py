import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "ui_ux",
    "problem_title": "Aesthetic Sovereignty Audit",
    "problem_context": """
    Audit the current CockpitPage.tsx (ICGL Dashboard). 
    Current State: Standard grid, basic cards, limited visual transparency of agent consultations.
    
    Mission: Upgrade the UI to reflect a 'Sovereign Council' aesthetic.
    Requirements:
    1. Visual transparency of the Inter-Agent Consultation loop (Builder, Sentinel, Steward).
    2. Immersive layout (Glassmorphism, Cyber-Sovereign theme).
    3. Clear representation of 'Autonomous Growth' and 'Self-Expansion' events.
    4. Enhanced Arabic typography and hierarchy.
    
    Propose a concrete design specification (components, colors, layout shifts).
    """,
}

try:
    response = requests.post(url, json=payload, timeout=90)
    data = response.json()
    print("UI/UX DESIGN PROPOSAL:")
    print("-" * 50)
    print(data.get("analysis", "NO PROPOSAL FOUND"))
    print("-" * 50)
    print("DESIGN RECOMMENDATIONS:")
    for rec in data.get("recommendations", []):
        print(f"  - {rec}")
except Exception as e:
    print(f"FAILED: {e}")
