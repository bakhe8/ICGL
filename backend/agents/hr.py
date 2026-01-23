from typing import Optional

from .base import Agent, AgentResult, AgentRole, Problem


class HRAgent(Agent):
    """
    HRAgent: Specialized in employee records, role definitions, and access mapping.
    """

    def __init__(self, llm_provider: Optional[any] = None):
        super().__init__(
            agent_id="hr",
            role=AgentRole.HR,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes problems from an HR perspective.
        """
        prompt = f"""
        Analyze the following problem from an HR and Organizational perspective:
        
        Title: {problem.title}
        Context: {problem.context}
        
        Focus on:
        1. Impact on existing role definitions.
        2. Necessary changes to access mapping or permissions.
        3. Human resource requirements or capacity shifts.
        4. Alignment with employee records/governance.
        
        Provide a detailed analysis, recommendations, and identify any HR-related concerns.
        """

        analysis_text = await self._ask_llm(prompt)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis_text,
            recommendations=[
                "Review role mapping in HDAL",
                "Verify access tokens for involved parties",
            ],
            concerns=["Potential permission drift detected in proposal context"]
            if "permission" in problem.context.lower()
            else [],
            confidence=0.85,
        )
