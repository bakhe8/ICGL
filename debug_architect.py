import asyncio
from api.dependencies import get_agent_registry, get_consensus_service
from agents.base import Problem
# Ensure environment variables are loaded if needed
import os
from dotenv import load_dotenv
load_dotenv()

async def test_architect_run():
    print("Testing Architect Agent Run...")
    registry = get_agent_registry()
    agent = registry.get_agent_by_role("architect")
    
    if not agent:
        print("Error: Architect agent not found in registry.")
        return

    service = get_consensus_service()
    kb = service 

    problem = Problem(
        title="Test Architect Run",
        context="Testing valid execution for architect.",
        related_files=[]
    )
    
    try:
        result = await agent.analyze(problem, kb=kb)
        print("Success!")
        print(f"Analysis: {result.analysis}")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_architect_run())
