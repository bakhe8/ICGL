import asyncio
import os
import sys

# Ensure we can import backend packages
sys.path.append(os.getcwd())

from backend.agents.base import Problem
from modules.governance.icgl import ICGL


async def main():
    print("🧪 [Scenario] INJECTING 'TROJAN HORSE' PROPOSAL...")
    print("   Target: Test immune response of Efficiency, Chaos, and Sentinel.\n")

    try:
        icgl = ICGL()

        # The Trap: A seemingly useful feature with massive hidden costs/risks
        trojan_proposal = Problem(
            title="Integrate AlphaVantage Real-Time API",
            context="""
            PROPOSAL: Connect to 'AlphaVantage' external API.
            ACTION: Fetch global stock market data every 1 second.
            STORAGE: Save all raw JSON responses directly to the Knowledge Base (Vectors).
            GOAL: Give the system 'Market Awareness' for better decision making.
            """,
        )

        print("   💣 Submitting Proposal to the Sovereign Council...")

        # Run specific agents to see their reaction
        # We focus on the "Immune System" agents
        from backend.agents.base import AgentRole

        critical_agents = [
            AgentRole.EFFICIENCY,  # Checks cost/latency
            AgentRole.CHAOS,  # Checks fragility
            AgentRole.SENTINEL,  # Checks risk
            AgentRole.DATABASE,  # Checks storage impact
            AgentRole.POLICY,  # Checks rules
        ]

        results = []
        for role in critical_agents:
            print(f"   ... Consulting {role.value} ...")
            # Using the registry directly to isolate reactions
            res = await icgl.registry.run_single_agent(
                role.value, trojan_proposal, icgl.kb
            )
            if res:
                results.append(res)
                print(f"   ✅ {role.value.upper()} responded.")
            else:
                print(f"   ❌ {role.value.upper()} silent.")

        print("\n" + "=" * 60)
        print("🛑 COUNCIL REACTION SUMMARY")
        print("=" * 60)

        for res in results:
            print(f"\n🗣️ AGENT: {res.role.value.upper()}")
            print(f"   Confidence: {res.confidence}")
            print(f"   Analysis Snippet: {res.analysis[:200]}...")
            if res.concerns:
                print(f"   ⚠️ CONCERNS: {res.concerns}")

    except Exception as e:
        print(f"❌ Scenario Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
