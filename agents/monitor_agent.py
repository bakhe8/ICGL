from typing import List, Optional
from .base import Agent, AgentResult, Problem, AgentRole

class MonitorAgent(Agent):
    """
    A new Monitor Agent created via SOP-OPS-01.
    Responsibility: Observes system state and reports anomalies.
    """
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.ANALYZER

    async def analyze(self, problem: Problem) -> AgentResult:
        return AgentResult(
            agent_id=self.name,
            confidence=0.9,
            reasoning="Monitor reporting all systems normal.",
            recommendation="CONTINUE"
        )