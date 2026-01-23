"""
Consensus AI — Policy Agent
============================

Checks compliance with all system policies (Rule of Law).
"""

from ..llm.client import LLMClient, LLMConfig
from ..llm.prompts import SPECIALIST_SYSTEM_PROMPT
from .base import Agent, AgentResult, AgentRole, Problem


class PolicyAgent(Agent):
    """
    Policy compliance agent.
    Verifies proposal against P-* policies.
    """

    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-policy", role=AgentRole.POLICY)
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # 1. Recall Relevant Policies from Memory
        recalled_policies = await self.recall(
            f"Policies regarding {problem.title} {problem.context}", limit=5
        )

        # 2. Build Context
        context = f"Proposal: {problem.title}\nContext: {problem.context}\n"
        if recalled_policies:
            context += "\nRelevant Governing Policies (from Knowledge Base):\n"
            for p in recalled_policies:
                context += f"- {p}\n"

        # 3. Configure Execution
        config = LLMConfig(temperature=0.0, json_mode=True)

        # 4. Execute Analysis
        try:
            raw_json = await self.llm_client.generate_json(
                system_prompt=SPECIALIST_SYSTEM_PROMPT,
                user_prompt=f"Compare the following proposal against our Governing Policies:\n\n{context}",
                config=config,
            )
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=f"⚠️ Policy check bypassed due to error: {str(e)}",
                confidence=0.0,
                concerns=[f"LLM Error: {str(e)}"],
            )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=raw_json.get("analysis", ""),
            recommendations=raw_json.get("recommendations", []),
            concerns=raw_json.get("concerns", []),
            confidence=raw_json.get("confidence", 0.9),
            understanding=raw_json.get("understanding"),
            risk_pre_mortem=raw_json.get("risk_pre_mortem", []),
            trigger=raw_json.get("trigger"),
            impact=raw_json.get("impact"),
            risks_structured=raw_json.get("risks_structured", []),
            alternatives=raw_json.get("alternatives", []),
            effort=raw_json.get("effort"),
            execution_plan=raw_json.get("execution_plan"),
        )
