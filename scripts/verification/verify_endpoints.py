import requests

BASE_URL = "http://127.0.0.1:8000"


def check(path, desc):
    url = f"{BASE_URL}{path}"
    print(f"Checking {desc}: {url}")
    try:
        r = requests.get(url)
        print(f"  Status: {r.status_code}")
        try:
            print(f"  Body: {r.json()}")
        except:
            print(f"  Body: {r.text[:100]}")

        if r.status_code == 200:
            print("  ✅ Success")
        elif r.status_code == 404:
            print("  ❌ Not Found (or matched wildcard?)")
            if "Analysis session context lost" in r.text:
                print("  ⚠️  Matched generic get_analysis(adr_id) handler!")
        else:
            print("  ⚠️  Other Error")

    except Exception as e:
        print(f"  Request Failed: {e}")


print("--- Verifying Endpoints ---")
check("/api/analysis/latest", "/api/analysis/latest")
check("/analysis/latest", "/analysis/latest (Root alias)")
check("/api/idea-summary/test-id", "/api/idea-summary (Expect 404 ADR not found)")
