"""
Consensus AI — Failure Agent
=============================

Analyzes potential failure modes and edge cases.
Uses 'Pre-Mortem' reasoning.
"""

from shared.python.agents.base import Agent, AgentResult, AgentRole, Problem
from shared.python.llm.client import LLMClient, LLMConfig
from shared.python.llm.prompts import FAILURE_SYSTEM_PROMPT


class FailureAgent(Agent):
    """
    Failure mode analysis agent.
    Asks: "How will this fail?"
    """

    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-failure", role=AgentRole.FAILURE)
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # 1. Setup Context
        intent = problem.intent
        context = f"SOVEREIGN GOAL: {intent.goal if intent else problem.title}\n"
        context += f"RISK LEVEL: {intent.risk_level if intent else 'UNKNOWN'}\n"
        if intent:
            context += f"ALLOWED FILES: {intent.allowed_files}\n"
            context += f"FORBIDDEN ZONES: {intent.forbidden_zones}\n"
            context += f"CONSTRAINTS: {intent.constraints}\n"
            context += f"MICRO-EXAMPLES: {intent.micro_examples}\n"

        # 2. Configure Execution
        config = LLMConfig(temperature=0.1, json_mode=True)

        # 3. Execute Analysis with Safety
        try:
            raw_json, usage = await self.llm_client.generate_json(
                system_prompt=FAILURE_SYSTEM_PROMPT,
                user_prompt=f"Please analyze this Intent Contract from a FAILURE perspective:\n\n{context}",
                config=config,
            )

            # Update Budget Tracking
            current_tokens = problem.metadata.get("total_tokens", 0)
            problem.metadata["total_tokens"] = current_tokens + usage.get("total_tokens", 0)
            problem.metadata["last_agent_tokens"] = usage.get("total_tokens", 0)
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=f"⚠️ Failure Analysis bypassed due to error: {str(e)}",
                confidence=0.0,
                concerns=[f"LLM Error: {str(e)}"],
            )

        # 4. Parse & Return
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=raw_json.get("analysis", ""),
            recommendations=raw_json.get("recommendations") or ["Consider failure mitigations"],
            concerns=raw_json.get("concerns") or ["No specific failure modes identified"],
            confidence=max(0.0, min(1.0, raw_json.get("confidence", 0.8))),
            understanding=raw_json.get("understanding"),  # Layer 2
            risk_pre_mortem=raw_json.get("risk_pre_mortem") or [],  # Layer 4
            trigger=raw_json.get("trigger"),
            impact=raw_json.get("impact"),
            risks_structured=raw_json.get("risks_structured") or [],
            alternatives=raw_json.get("alternatives") or [],
            effort=raw_json.get("effort"),
            execution_plan=raw_json.get("execution_plan"),
        )
