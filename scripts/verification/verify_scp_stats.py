import requests

BASE_URL = "http://127.0.0.1:8000"


def check_endpoint(path, name):
    url = f"{BASE_URL}{path}"
    print(f"Checking {name}: {url}")
    try:
        r = requests.get(url)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Response Keys: {list(data.keys())}")
            if "data" in data:
                print(f"  Data Keys: {list(data['data'].keys())}")
            elif "stats" in data:
                print(f"  Stats Keys: {list(data['stats'].keys())}")
            else:
                print(f"  Root Keys: {list(data.keys())}")
            print("  ✅ Success")
        else:
            print("  ❌ Failed")
            print(f"  Response: {r.text[:100]}")
    except Exception as e:
        print(f"  Exception: {e}")


print("--- Verifying SCP Overview Endpoints ---")
check_endpoint("/channels/stats", "Channels Stats")
check_endpoint("/observability/stats", "Observability Stats")
