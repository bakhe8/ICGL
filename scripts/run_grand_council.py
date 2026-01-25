import json
import sys

import requests

API_URL = "http://127.0.0.1:8000/api/governance/simulate-council"

TOPIC = "System Evolution & Future Development Requirements (2026)"
CONTEXT = """
The Current Roadmap (Phases 1-11) is complete. 
The system has:
1. Stable Architecture & Full Agent Pool.
2. Calm Sovereign UI.
3. Executive Agent (Human Bridge) & Signing Queue.
4. Proof-of-Benefit Framework.

QUESTION TO ALL AGENTS:
From your specific perspective (e.g., Security, Database, UX, Policy), what is the SINGLE most critical development or upgrade required next? 
Do not be polite. Be technical and demanding about your domain needs.
"""


def run_council():
    print(f"🚀 Convening Grand Council on: {TOPIC}...")
    try:
        response = requests.post(API_URL, json={"topic": TOPIC, "context": CONTEXT})
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        print(f"✅ Received input from {len(results)} agents.")

        # Save raw output
        with open("data/council_output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("💾 Saved raw output to data/council_output.json")
        return results

    except Exception as e:
        print(f"❌ Council Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_council()
