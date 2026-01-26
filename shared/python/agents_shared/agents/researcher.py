from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class ResearcherAgent(Agent):
    """
    The Scientific Researcher.
    Specialized in analyzing past interventions, failures, and successes
    to propose evolutionary policy changes.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="researcher", role=AgentRole.RESEARCHER, llm_provider=llm_provider
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        prompt = f"""
        You are the Scientific Researcher (The Intelligence Engine).
        Your Job: Look for patterns in past decisions ({problem.title}) 
        and propose a POLICY_UPDATE if current rules are outdated.
        
        Context: {problem.context}
        
        Search for:
        1. Institutional Memory Drift.
        2. Potential for automated rule enforcement.
        3. Areas where human intervention was required but could be systemic.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            confidence=0.85,
            recommendations=["Update policy P-AUTO-01", "Enhance sentinel detection"],
            metadata={"research_focus": "evolution"},
        )
