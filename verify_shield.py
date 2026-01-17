import asyncio
from icgl.agents.base import Agent, AgentRole, Problem, AgentResult
from icgl.core.observability import SystemObserver

class BrokenAgent(Agent):
    def __init__(self):
        super().__init__("agent-broken", AgentRole.FAILURE)
        self.observer = SystemObserver() # Enable metrics
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        raise ValueError("Simulated Critical Failure!")

async def test_shield():
    print("🛡️ Testing Stability Shield...")
    
    agent = BrokenAgent()
    problem = Problem("Test Crash", "Context")
    
    # This should NOT raise an exception
    result = await agent.analyze(problem, None)
    
    if result.confidence == 0.0 and "Simulated Critical Failure" in result.analysis:
        print("✅ Shield ACTIVATED. Exception caught.")
        print(f"   Fallback Analysis: {result.analysis}")
    else:
        print(f"❌ Shield FAILED. Result: {result}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(test_shield())
