import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def approve_all():
    print("🚀 Approving all pending decisions...")
    
    # IDs of the mock proposals in server.py (0, 1, 2)
    decision_ids = [0, 1, 2]
    
    for i in decision_ids:
        url = f"{BASE_URL}/proposals/{i}"
        payload = {"status": "APPROVED"}
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print(f"✅ Decision {i} APPROVED successfully.")
            else:
                print(f"❌ Failed to approve {i}: {response.text}")
        except Exception as e:
            print(f"⚠️ Error approving {i}: {e}")

if __name__ == "__main__":
    approve_all()
