from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class PerformanceAnalyzerAgent(Agent):
    """
    The Performance Analyzer.
    Specialized in deep CPU/RAM and runtime profiling.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="performance-analyzer",
            role=AgentRole.PERFORMANCE_ANALYZER,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        prompt = f"""
        You are the Performance Analyzer (The Metric Eye).
        Analyze the following problem specifically for:
        1. CPU Complexity (Big O).
        2. Memory leaks or high retention zones.
        3. SQLite query performance (missing indices).
        
        Context: {problem.context}
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            confidence=0.9,
            recommendations=["Optimize query path", "Buffer memory allocation"],
            metadata={"metric_focus": "performance"},
        )
