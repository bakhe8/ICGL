import sys

import requests

try:
    print("Checking OpenAPI Schema...")
    r = requests.get("http://127.0.0.1:8000/openapi.json")
    if r.status_code != 200:
        print(f"Failed to fetch schema: {r.status_code}")
        sys.exit(1)

    schema = r.json()
    paths = schema.get("paths", {})

    found_latest = "/api/analysis/latest" in paths
    found_summary = "/api/idea-summary/{adr_id}" in paths

    print(f"/api/analysis/latest: {'✅ Found' if found_latest else '❌ Missing'}")
    print(f"/api/idea-summary/{{adr_id}}: {'✅ Found' if found_summary else '❌ Missing'}")

    if not found_latest:
        print("\nExisting /api/analysis paths:")
        for p in paths.keys():
            if "analysis" in p:
                print(f" - {p}")

except Exception as e:
    print(f"Error: {e}")
