import asyncio
import os
import sys

# Ensure we can import backend packages
sys.path.append(os.getcwd())

from backend.agents.base import Problem
from backend.governance.icgl import ICGL


async def main():
    print("🎙️ [System] CALLING ALL AGENTS TO THE TOWN HALL...")
    print("   (This creates a temporary ICGL instance to poll the collective mind)\n")

    try:
        # Initialize the Sovereign Loop
        # This loads Registry, KnowledgeBase, and all Agents (including new ones)
        icgl = ICGL()

        # Create the Audit Problem (The "Town Hall" Question)
        audit_problem = Problem(
            title="System Consciousness Audit (Town Hall)",
            context="""
            The User has requested a comprehensive 'System Consciousness Test'.
            
            DIRECTIVE TO ALL AGENTS:
            1. Report your operational status.
            2. Identify your top concern regarding the system's current state.
            3. Make one request to the Human or the Council.
            
            SPECIFIC INQUIRIES:
            - @DatabaseArchitect: How is our memory structure?
            - @EfficiencyAgent: Are we bloated?
            - @ChaosAgent: What is the most dangerous theoretical vulnerability right now?
            - @HRAgent: Is the team balanced?
            
            Speak freely. Transparency is absolute.
            """,
        )

        print("   🤖 Agents receiving audit directive...")

        # Run the cycle directly via Registry
        # We explicitly want to hear from everyone, so we use run_all
        results = await icgl.registry.run_all(audit_problem, icgl.kb)

        # Synthesize into the final report
        synthesis = icgl.registry._synthesize(results)

        print("\n" + "=" * 60)
        print(synthesis.to_markdown())
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"❌ Town Hall Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Check for API Key
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "⚠️ WARNING: OPENAI_API_KEY not found in env. Agents may default to Mock mode."
        )

    asyncio.run(main())
