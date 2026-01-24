import asyncio
import json

from backend.agents.base import AgentRole, Problem
from backend.governance.icgl import ICGL


async def main():
    # Load env for API keys
    from dotenv import load_dotenv

    load_dotenv()

    icgl = ICGL()
    registry = icgl.registry

    # 1. Define the Problem: Global Role Overlap Audit
    # We provide descriptions of all agents to the Mediator
    agent_descriptions = []
    for role in AgentRole:
        agent = registry.get_agent(role)
        if agent:
            # Simple summary of each agent's purpose
            agent_descriptions.append(
                {
                    "agent_id": agent.agent_id,
                    "role": role.value,
                    "analysis": f"Specializes in {getattr(agent, 'specialty', 'general ' + role.value)}. Focuses on {agent.__doc__ or 'N/A'}",
                    "confidence": 1.0,
                }
            )

    problem = Problem(
        title="Institutional Audit: Role Overlap & Boundary Tensions",
        context="Analyze the roster of 22 agents for potential redundancy, conflicting mandates, or coordination gaps.",
        metadata={"agent_results": agent_descriptions},
    )

    # 2. Invoke Mediator
    mediator = registry.get_agent(AgentRole.MEDIATOR)
    if not mediator:
        print("Mediator not found.")
        return

    print("Calling Mediator for Audit...")
    result = await mediator.analyze(problem, icgl.kb)

    # Output the result to a temporary file for the assistant to read
    with open("mediator_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "analysis": result.analysis,
                "recommendations": result.recommendations,
                "tensions": getattr(result, "tensions", []),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("Report generated: mediator_audit_report.json")


if __name__ == "__main__":
    asyncio.run(main())
