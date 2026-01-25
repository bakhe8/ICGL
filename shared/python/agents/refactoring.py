"""
Consensus AI — Refactoring Agent
=================================

Specialized in code quality, patterns, and structural optimization.
Reviews Builder output and suggests technical debt reduction.
"""

from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class RefactoringAgent(Agent):
    """
    The Refactoring Agent: Fills the gap for structural code improvement.
    Specializes in identifying code smells and applying design patterns.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-refactoring",
            role=AgentRole.REFACTORING,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Structural cleanup and pattern optimization analysis.
        Formalizes the 'Refactoring Loop' by consulting Builder and Testing.
        """
        # 1. Consult Builder for Impact Analysis
        builder_result = await self.consult_peer(
            AgentRole.BUILDER,
            title=f"Refactoring Impact: {problem.title}",
            context=problem.context,
            kb=kb,
        )
        builder_report = (
            builder_result.analysis
            if builder_result
            else "No builder impact report available."
        )

        # 2. Consult Testing for Safety Guards
        testing_result = await self.consult_peer(
            AgentRole.TESTING,
            title=f"Refactoring Safety: {problem.title}",
            context=f"Proposed Context: {problem.context}\nImpact Report: {builder_report}",
            kb=kb,
        )
        testing_report = (
            testing_result.analysis
            if testing_result
            else "No testing safety report available."
        )

        prompt = f"""
        Analyze the following code/problem for refactoring opportunities as the REFACTORING agent:
        
        Title: {problem.title}
        Context: {problem.context}
        
        🛠️ BUILDER IMPACT REPORT:
        {builder_report}
        
        🧪 TESTING SAFETY REPORT:
        {testing_report}
        
        Tasks:
        1. Identification of code smells (duplication, complexity).
        2. Application of design patterns (SOLID, DRY).
        3. Harmonize refactoring with Builder's impact constraints.
        4. Address any 'Silent Failures' or testing gaps identified.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Apply Clean Code principles aligned with Builder impact",
                "Ensure new patterns pass testing safety thresholds",
                "Verify architectural alignment with Knowledge Steward",
            ],
            confidence=0.92,
            references=[builder_report, testing_report],
        )
