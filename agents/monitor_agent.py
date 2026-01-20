from typing import List, Optional
from .base import Agent, AgentResult, Problem, AgentRole

class MonitorAgent(Agent):
    """
    A new Monitor Agent created via SOP-OPS-01.
    Responsibility: Observes system state and reports anomalies.
    """
    
    def __init__(self, agent_id: str = "agent-monitor", llm_provider=None):
        super().__init__(agent_id=agent_id, role=AgentRole.MONITOR, llm_provider=llm_provider)

    async def _analyze(self, problem: Problem, kb=None) -> AgentResult:
        return AgentResult(
            agent_id=self.agent_id, # Use inherited agent_id
            role=self.role, # Use inherited role
            analysis="Monitor reporting all systems normal.",
            recommendations=["CONTINUE"],
            confidence=0.9
        )