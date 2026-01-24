import json
import time

import requests

BASE_URL = "http://127.0.0.1:8000/api/nexus"


def test_purpose_gate_rejection():
    print("\n[TEST 1] Testing Purpose Gate: Rejection of High Complexity")
    print("-" * 50)
    payload = {
        "idea": "I propose a massive self-evolving blockchain layer that rewrites the system kernel every 5 minutes to achieve peak sovereign awakening and cosmic alignment."
    }
    res = requests.post(f"{BASE_URL}/propose", json=payload)
    print(f"Status: {res.status_code}")
    print("Response:")
    print(json.dumps(res.json(), indent=2))


def test_purpose_gate_approval():
    print("\n[TEST 2] Testing Purpose Gate: Approval of Lean Optimization")
    print("-" * 50)
    payload = {
        "idea": "I propose an optimization of the index.css by removing 10 unused glassmorphic classes to improve rendering performance and reduce complexity."
    }
    res = requests.post(f"{BASE_URL}/propose", json=payload)
    print(f"Status: {res.status_code}")
    print("Response:")
    print(json.dumps(res.json(), indent=2))
    return res.json().get("adr_id")


if __name__ == "__main__":
    try:
        test_purpose_gate_rejection()
        time.sleep(2)
        test_purpose_gate_approval()
    except Exception as e:
        print(f"FAILED: {e}")
