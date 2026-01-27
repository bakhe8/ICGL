import requests

BASE_URL = "http://127.0.0.1:8000"


def check(path, desc):
    url = f"{BASE_URL}{path}"
    print(f"Checking {desc}: {url}")
    try:
        r = requests.get(url)
        print(f"  Status: {r.status_code}")
        try:
            body = r.json()
            alerts = body.get("data", {}).get("alerts", [])
            print(f"  Alerts Count: {len(alerts)}")
            if len(alerts) > 0:
                print(f"  First Alert Pattern: {alerts[0].get('pattern')}")
        except:
            print(f"  Body: {r.text[:100]}")

        if r.status_code == 200:
            print("  ✅ Success")
        elif r.status_code == 404:
            print("  ❌ Not Found")
        else:
            print("  ⚠️  Other Error")

    except Exception as e:
        print(f"  Request Failed: {e}")


print("--- Verifying Security Endpoints ---")
check("/patterns/alerts?limit=20", "/patterns/alerts")
