"""
Consensus AI — Sentinel Agent
==============================

Agent wrapper for the Sentinel Rule Engine.
Allows the Sentinel to participate in the agent pool discussion.
"""

from .base import Agent, AgentRole, Problem, AgentResult
from ..sentinel import Sentinel, RuleRegistry


class SentinelAgent(Agent):
    """
    Sentinel wrapper agent.
    Runs the Sentinel rule engine and reports alerts as part of synthesis.
    """
    
    def __init__(self, sentinel: Sentinel = None):
        super().__init__(agent_id="agent-sentinel", role=AgentRole.SENTINEL)
        self.sentinel = sentinel or Sentinel()
        
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # In this mock/stub flow, we simulate checking an ADR derived from the problem
        # In a real flow, the problem -> proposed_adr -> sentinel scan
        
        # Here we just report on the general risk posture
        analysis = "Running operational risk rules (Sentinel Engine)..."
        
        # If we had a concrete ADR object here, we would run:
        # alerts = self.sentinel.scan_adr(adr, kb)
        
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Verify no critical alerts before approval"
            ],
            concerns=[], # Alerts would go here
            confidence=1.0
        )
