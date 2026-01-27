import json
import urllib.request

ENDPOINTS = [
    ("system_agents", "http://127.0.0.1:8000/api/system/agents"),
    ("governance_proposals", "http://127.0.0.1:8000/api/governance/proposals"),
    ("executive_queue", "http://127.0.0.1:8000/api/executive/queue"),
]

for name, url in ENDPOINTS:
    print(f"--- {name} ({url}) ---")
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            status = r.getcode()
            body = r.read().decode("utf-8")
            try:
                data = json.loads(body)
                print("STATUS:", status)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception:
                print("STATUS:", status)
                print(body)
    except Exception as e:
        print("ERROR:", str(e))
    print()
