"""
Consensus AI — DevOps Agent
===========================

Specialized in environment stability, CI/CD simulation, and deployment hygiene.
Ensures that code changes are compatible with the target runtime and infrastructure.
"""

import os
from typing import Any, Optional

import psutil

from .base import Agent, AgentResult, AgentRole, Problem


class DevOpsAgent(Agent):
    """
    The DevOps Agent: Manages the 'Operational Gate'.
    Phase 5 Sovereign Demand fulfillment.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="agent-devops",
            role=AgentRole.DEVOPS,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Operational analysis: Environment check + Deployment Impact.
        """
        # 1. Environment Snapshot
        env_report = self._get_environment_snapshot()

        # 2. Consult Sentinel for resource baseline
        sentinel_result = await self.consult_peer(
            AgentRole.GUARDIAN_SENTINEL,
            title="Resource Baseline for DevOps",
            context=f"Checking environment for: {problem.title}",
            kb=kb,
        )
        resource_context = (
            sentinel_result.analysis if sentinel_result else "Resources unknown."
        )

        prompt = f"""
        Analyze the following problem from a DEVOPS perspective:
        
        Title: {problem.title}
        Context: {problem.context}
        
        🚀 ENVIRONMENT SNAPSHOT:
        {env_report}
        
        📊 RESOURCE CONTEXT (from Sentinel):
        {resource_context}
        
        Tasks:
        1. Evaluate if code changes pose a deployment risk (memory leaks, port conflicts).
        2. Determine if the environment needs configuration updates.
        3. Identify any CI/CD automation gaps that this change might create/fix.
        """

        analysis = await self._ask_llm(prompt, problem)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "Verify environment variables before deployment",
                "Ensure health check endpoints are preserved",
                "Log all deployment-impacting changes to the Executive Registry",
            ],
            confidence=0.90,
            references=[env_report, resource_context],
        )

    def _get_environment_snapshot(self) -> str:
        """Simulates environment check by reading OS and process info."""
        try:
            os_name = os.name
            cpu_count = os.cpu_count()
            mem = psutil.virtual_memory()

            report = f"OS: {os_name} | CPUs: {cpu_count} | Mem Total: {mem.total / (1024**3):.1f}GB"
            report += f" | Available: {mem.available / (1024**3):.1f}GB"
            return report
        except Exception as e:
            return f"Env snapshot failed: {str(e)}"
