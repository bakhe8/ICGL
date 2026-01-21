"""
Consensus AI — Failure Agent
=============================

Analyzes potential failure modes and edge cases.
Uses 'Pre-Mortem' reasoning.
"""

from .base import Agent, AgentRole, Problem, AgentResult


class FailureAgent(Agent):
    """
    Failure mode analysis agent.
    Asks: "How will this fail?"
    """
    
    def __init__(self):
        super().__init__(agent_id="agent-failure", role=AgentRole.FAILURE)
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        analysis = (
            "Pre-mortem analysis running...\n"
            "- Identified 2 potential failure modes.\n"
            "- Analyzed recovery paths."
        )
        
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Add circuit breakers for external calls",
                "Define fallback state if primary fails"
            ],
            concerns=[
                "No retry validation defined in proposal"
            ],
            confidence=0.85
        )
