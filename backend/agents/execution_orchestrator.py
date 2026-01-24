from typing import Any, Optional

from .base import Agent, AgentResult, AgentRole, Problem


class ExecutionOrchestratorAgent(Agent):
    """
    The Execution Orchestrator.
    Coordinates between Builder and Engineer to ensure atomic execution
    of code changes and prevent git-level conflicts.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="execution-orchestrator",
            role=AgentRole.EXECUTION_ORCHESTRATOR,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        prompt = f"""
        You are the Execution Orchestrator (The Conductor).
        Your Job: Map out the exact commit sequence and file system locks needed.
        
        Title: {problem.title}
        Context: {problem.context}
        
        Focus on:
        1. Atomic commits (all or nothing).
        2. Sequence: Which files must be written before others?
        3. Environment Verification: Checking if the env is ready for deployment.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            confidence=0.95,
            recommendations=["Execute atomic commit", "Lock repository for write"],
            metadata={"execution_flow": "atomic"},
        )
