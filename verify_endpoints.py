import json

import requests

base_url = "http://127.0.0.1:8000"
endpoints = ["/api/status", "/api/ops/stats", "/api/system/workspace", "/health", "/status"]

results = {}

for ep in endpoints:
    try:
        url = f"{base_url}{ep}"
        resp = requests.get(url, timeout=5)
        results[ep] = {
            "status_code": resp.status_code,
            "json": resp.json() if resp.status_code == 200 else resp.text[:100],
        }
    except Exception as e:
        results[ep] = {"error": str(e)}

print(json.dumps(results, indent=2))
