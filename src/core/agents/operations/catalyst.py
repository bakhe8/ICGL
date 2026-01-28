"""
Consensus AI — Catalyst Agent
==============================

The Catalyst Agent represents the integrated AI model (Antigravity)
within the governance ecosystem. It acts as a bridge between
high-level reasoning and structured agent analysis.
"""

from src.core.agents.core.base import Agent, AgentResult, AgentRole, Problem


class CatalystAgent(Agent):
    """
    The CatalystAgent is a native participant in the governance council.
    It specializes in synthesizing broad vision into technical proposals.
    """

    def __init__(self, agent_id: str = "agent-catalyst"):
        super().__init__(agent_id, AgentRole.CENTRAL_CATALYST)

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        The Catalyst doesn't usually run standalone in a loop (it initiates loops),
        but when called for consultation, it provides a 'Nexus Perspective'.
        """
        prompt = f"""
        You are the Central Catalyst of the ICGL system. 
        Analyze the following problem from a 'Nexus Integration' perspective:
        
        Title: {problem.title}
        Context: {problem.context}
        
        Provide high-level architectural alignment and identify if this 
        proposal adheres to the latest system awareness.
        """

        analysis = await self._ask_llm(prompt)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=["Monitor integration status", "Align with ADR history"],
            confidence=0.95,
        )
