import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def reset_and_execute():
    # 1. Reset all to NEW
    print("🔄 Resetting decision states...")
    decision_ids = [0, 1, 2]
    for i in decision_ids:
        requests.put(f"{BASE_URL}/proposals/{i}", json={"status": "NEW", "details": ""})

    print("⏳ Waiting for backend reset...")
    time.sleep(1)

    # 2. Approve all to trigger REAL execution
    print("🚀 Triggering REAL EXECUTION (Approving)...")
    for i in decision_ids:
        requests.put(f"{BASE_URL}/proposals/{i}", json={"status": "APPROVED"})
        print(f"✅ Approved Decision {i}")

if __name__ == "__main__":
    reset_and_execute()
