"""
Consensus AI — Efficiency Expert Agent (The 4th Eye)
===================================================

"The System cannot think infinitely; it must think efficiently."

Roles:
1. Economic Guardian: Monitors Token Budget vs ROI.
2. Latency Killer: Suggests parallelization or caching.
3. Garbage Collector: Identifies obsolete Knowledge (Vectors/ADRs).
"""

from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class EfficiencyAgent(Agent):
    """
    The Efficiency Expert.
    Ensures the system remains lean, fast, and economically viable.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-efficiency",
            role=AgentRole.EFFICIENCY,  # To be added to Enum
            llm_provider=llm_provider,
        )
        self.specialty = "optimization"

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Analyzes the problem/Code for inefficiency.
        """
        # 1. Social Discovery: Check if we have budget data
        # We can inspect the Registry to see if a Budget Manager is active,
        # or just inspect the problem metadata directly.

        current_tokens = problem.metadata.get("total_tokens", 0)

        prompt = f"""
        You are the Efficiency Expert.
        Your Goal: Minimize Waste (Tokens, Time, Complexity).
        
        Analyze:
        Title: {problem.title}
        Context: {problem.context}
        Current Token Usage: {current_tokens}
        
        Tasks:
        1. Detect "Bloat": Is the prompt too long? Are we sending unnecessary context?
        2. Detect "Latency": Can this be parallelized?
        3. Detect "Obscolescence": Are we relying on old ADRs that should be pruned?
        
        Output specific, actionable reduction strategies.
        """

        analysis = await self._ask_llm(prompt, problem)

        recommendations = []
        concerns = []

        # Heuristics
        if len(problem.context) > 10000:
            concerns.append(
                "Context Overflow Risk: Input context is extremely large (>10k chars)."
            )
            recommendations.append(
                "Apply 'Context Compression' or 'Refinement' before processing."
            )

        if current_tokens > 40000:
            concerns.append("Critical Budget Warning: Approaching 50k limit.")
            recommendations.append("HALT non-essential agents immediately.")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=recommendations,
            concerns=concerns,
            confidence=0.90,
        )

    async def garbage_collect(self) -> str:
        """
        Unique Capability: Scans KB for low-value assets.
        To be called by a Scheduler or Admin.
        """
        # Mock logic for Phase 1 (Real logic would query VectorDB scores)
        return "Garbage Collection Scan: No obsolete vectors found (Mock)."
