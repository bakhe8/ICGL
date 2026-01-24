import asyncio
import json

from dotenv import load_dotenv

from backend.agents.base import Problem
from backend.governance.icgl import ICGL


async def main():
    load_dotenv()

    icgl = ICGL()
    registry = icgl.registry
    roles = registry.list_agents()

    print(f"🚀 Initializing Grand Council of {len(roles)} Agents...")

    roadmap_proposal = {}

    for role in roles:
        agent = registry.get_agent(role)
        if not agent:
            continue

        role_label = role.value if hasattr(role, "value") else str(role)
        print(f"--- [COUNCIL] Consulting: {role_label} ---")

        problem = Problem(
            title="Sovereign Roadmap 2026: The Path to Ultra-Specialization",
            context="""
            The ICGL system has reached Phase 7 with 27 specialized agents. 
            The goal is to define the next major evolution. 
            From YOUR niche perspective, what should be our TOP priority for the next 6 months? 
            Propose one specific feature or structural change that would maximize system-wide harmony and performance.
            """,
            metadata={},
        )

        try:
            result = await agent.analyze(problem, icgl.kb)
            roadmap_proposal[role_label] = {
                "vision": result.analysis,
                "top_priority": result.recommendations[0]
                if result.recommendations
                else "N/A",
                "risk": result.concerns[0] if result.concerns else "N/A",
            }
        except Exception as e:
            print(f"❌ Error with {role_label}: {e}")

    with open("grand_roadmap_data.json", "w", encoding="utf-8") as f:
        json.dump(roadmap_proposal, f, indent=2, ensure_ascii=False)

    print("✅ Meeting complete. Processing synthesis...")


if __name__ == "__main__":
    asyncio.run(main())
