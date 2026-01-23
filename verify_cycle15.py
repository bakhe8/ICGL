import sys
import time

import requests

BASE_URL = "http://localhost:8000"


def verify():
    print("🚀 Sending 'Simple Documentation Update' Request...")
    # This should trigger a small council (Archivist, Documentation)
    idea = "Update the README to include installation instructions for the new API."

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
            synthesis = analysis.get("synthesis")

            if synthesis:
                agent_results = synthesis.get("agent_results", [])

                # Check Architect
                architect = next(
                    (r for r in agent_results if r["agent_id"] == "agent-architect"),
                    None,
                )
                if not architect:
                    print("❌ Architect result missing!")
                    return

                required = architect.get("required_agents", [])
                rationale = architect.get("summoning_rationale")

                print("\n✨ Architect Analysis Received!")
                print(f"   🏛️  Summoned Council: {required}")
                print(f"   📜  Rationale: {rationale}")

                # Check actual agents present in result (excluding Architect/Secretary/Mediator)
                present_agents = [
                    r["agent_id"]
                    for r in agent_results
                    if r["agent_id"]
                    not in ["agent-architect", "secretary", "agent-mediator"]
                ]

                print(f"   🤖 Actual Agents Ran: {present_agents}")

                # Verify Filtering Logic
                # Logic: present_agents should be a subset of (required + Sentinel/Policy if forced)
                # Ideally, for this request, 'failure' or 'hr' should NOT be here if not summoned.

                if "hr" in present_agents and "hr" not in required:
                    print("❌ ERROR: HR Agent ran but was not summoned!")
                elif (
                    len(present_agents) < 10
                ):  # Assuming we have 17 agents, < 10 means filtering worked
                    print(
                        "✅ Dynamic Filtering Successful (Council is smaller than full roster)."
                    )
                else:
                    print("⚠️ Warning: Full roster might have run. Check logs.")

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
