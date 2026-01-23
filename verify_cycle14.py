import sys
import time

import requests

BASE_URL = "http://localhost:8000"


def verify():
    print("🚀 Sending Ambiguous Arabic Request...")
    idea = "أريد النظام يكون خفيف عالقل"

    try:
        # 1. Start Idea Run
        res = requests.post(f"{BASE_URL}/api/idea-run", json={"idea": idea})
        if res.status_code != 200:
            print(f"❌ Failed to start run: {res.text}")
            return

        data = res.json()
        adr_id = data.get("adr_id")
        print(f"✅ Run Started. ADR ID: {adr_id}")

        # 2. Poll for Results
        print("⏳ Polling for analysis...")
        max_retries = 30
        for i in range(max_retries):
            res = requests.get(f"{BASE_URL}/api/analysis/{adr_id}")
            if res.status_code != 200:
                print(f"⚠️ Poll error: {res.status_code}")
                continue

            analysis = res.json()
            status = analysis.get("status")

            # Check Secretary Result if synthesis exists
            synthesis = analysis.get("synthesis")
            if synthesis:
                results = synthesis.get("agent_results", [])
                secretary = next(
                    (r for r in results if r["agent_id"] == "secretary"), None
                )
                architect = next(
                    (r for r in results if r["agent_id"] == "agent-architect"), None
                )

                if secretary:
                    interp = secretary.get("interpretation_ar")
                    intent = secretary.get("english_intent") or secretary.get(
                        "technical_intent"
                    )
                    ambiguity = secretary.get("ambiguity_level")

                    if interp:
                        print("\n✨ Secretary Verification Successful!")
                        print(f"   🪞 Interpretation (AR): {interp}")
                        print(f"   📝 Technical Intent: {intent}")
                        print(f"   ⚖️ Ambiguity: {ambiguity}")

                        if architect:
                            # We can't easily see internal state of Architect, but if Architect produced analysis
                            # based on this intent, we assume success.
                            # Ideally check if Architect references the intent.
                            print(
                                f"\n🏗️ Architect Analysis Confidence: {architect.get('confidence')}"
                            )
                        return

            if status == "failed":
                print(f"❌ Analysis Failed: {analysis.get('error')}")
                return

            time.sleep(1)
            sys.stdout.write(".")
            sys.stdout.flush()

        print("\n❌ Timed out waiting for analysis.")

    except Exception as e:
        print(f"\n❌ Exception: {e}")


if __name__ == "__main__":
    verify()
