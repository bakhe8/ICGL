from typing import Any, Optional

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem


class SecurityOrchestratorAgent(Agent):
    """
    The Security Orchestrator.
    Consolidates risk reports from Guardian, Sentinel, and Chaos agents
    into a single authoritative security verdict.
    """

    def __init__(self, llm_provider: Optional[Any] = None):
        super().__init__(
            agent_id="security-orchestrator",
            role=AgentRole.SECURITY_ORCHESTRATOR,
            llm_provider=llm_provider,
        )

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # Collect peer reviews
        guardian_res = await self.consult_peer(AgentRole.GUARDIAN, problem.title, problem.context, kb)
        sentinel_res = await self.consult_peer(AgentRole.SENTINEL, problem.title, problem.context, kb)
        chaos_res = await self.consult_peer(AgentRole.CHAOS, problem.title, problem.context, kb)

        prompt = f"""
        You are the Security Orchestrator (The Unified Shield).
        Your Job: Synthesize competing security perspectives into one final verdict.
        
        Guardian Reports: {guardian_res.analysis if guardian_res else "No report"}
        Sentinel Reports: {sentinel_res.analysis if sentinel_res else "No report"}
        Chaos Reports: {chaos_res.analysis if chaos_res else "No report"}
        
        Context: {problem.context}
        
        Requirements:
        1. Resolve conflicts between "Safety" and "Speed".
        2. Provide a single "Status" (PASS/WARN/BLOCK).
        3. Explain the consensus or the tie-break rationale.
        """

        analysis = await self._ask_llm(prompt)

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            confidence=0.98,
            recommendations=["Follow unified security protocol"],
            metadata={"verdict": "unified_security"},
        )
