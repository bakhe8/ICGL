import asyncio
import json

from backend.agents.base import Problem
from backend.governance.icgl import ICGL


async def main():
    # Load env for API keys
    from dotenv import load_dotenv

    load_dotenv()

    icgl = ICGL()
    registry = icgl.registry

    # Read the target report
    report_path = r"C:\Users\Bakheet\.gemini\antigravity\brain\63a59771-a351-4d43-81a7-583d8253bd88\system_gaps_audit.md"
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
    except Exception as e:
        print(f"Failed to read report: {e}")
        return

    # List all roles to iterate
    roles = registry.list_agents()

    individual_reviews = {}

    for role in roles:
        agent = registry.get_agent(role)
        if not agent:
            continue

        role_label = role.value if hasattr(role, "value") else str(role)
        print(f"--- Consulting Agent: {role_label} ---")

        problem = Problem(
            title=f"Review of Systemic Gaps Report: {role_label} Perspective",
            context=f"The following is a draft of the 'System Gaps Audit'. Review it from YOUR unique perspective. Add specific gaps you've noticed, propose enhancements to existing sections, and suggest how to improve cooperation with other agents.\n\nREPORT CONTENT:\n{report_content}",
            metadata={},
        )

        try:
            # Perform targeted analysis
            result = await agent.analyze(problem, icgl.kb)

            individual_reviews[role_label] = {
                "agent_id": agent.agent_id,
                "analysis": result.analysis,
                "recommendations": result.recommendations,
                "concerns": result.concerns,
            }
        except Exception as e:
            print(f"Error consulting {role_label}: {e}")
            individual_reviews[role_label] = {"error": str(e)}

    # Save all results
    output_path = "multilateral_review_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(individual_reviews, f, indent=2, ensure_ascii=False)

    print(f"Multilateral review complete. Data saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
