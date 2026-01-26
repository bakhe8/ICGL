"""
Consensus AI — Concept Guardian
================================

Protects semantic integrity of concepts.
Prevents "Definition Drift".
"""

from modules.llm.client import LLMClient, LLMConfig
from modules.llm.prompts import SPECIALIST_SYSTEM_PROMPT
from .base import Agent, AgentResult, AgentRole, Problem


class ConceptGuardian(Agent):
    """
    Concept integrity agent.
    Ensures no implicit redefinition of terms.
    Reference: P-GOV-09
    """

    def __init__(self, llm_provider=None):
        super().__init__(agent_id="agent-guardian", role=AgentRole.GUARDIAN)
        self.llm_client = LLMClient()

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        # 1. Recall Relevant Concepts
        recalled_concepts = await self.recall(
            f"Concepts related to {problem.title}", limit=5
        )

        # 2. Build Context
        intent = problem.intent
        context = f"SOVEREIGN GOAL: {intent.goal if intent else problem.title}\n"
        if recalled_concepts:
            context += "\nRelevant Concepts (from Knowledge Base):\n"
            for c in recalled_concepts:
                context += f"- {c}\n"

        # 3. Configure Execution
        config = LLMConfig(temperature=0.1, json_mode=True)

        # 4. Execute Analysis with Safety
        try:
            raw_json, usage = await self.llm_client.generate_json(
                system_prompt=SPECIALIST_SYSTEM_PROMPT,
                user_prompt=(
                    f"You are the Concept Guardian. Analyze this Intent Contract for semantic integrity:\n\n"
                    f"{context}\n\n"
                    f"Does this proposal redefine existing concepts? Does it introduce 'Definition Drift'?"
                ),
                config=config,
            )

            # Update Budget Tracking
            current_tokens = problem.metadata.get("total_tokens", 0)
            problem.metadata["total_tokens"] = current_tokens + usage.get(
                "total_tokens", 0
            )
            problem.metadata["last_agent_tokens"] = usage.get("total_tokens", 0)
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                analysis=f"⚠️ Concept integrity check bypassed due to error: {str(e)}",
                confidence=0.0,
                concerns=[f"LLM Error: {str(e)}"],
            )

        # 5. Return Result
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=raw_json.get("analysis", ""),
            recommendations=raw_json.get("recommendations", []),
            concerns=raw_json.get("concerns", []),
            confidence=raw_json.get("confidence", 0.9),
            understanding=raw_json.get("understanding"),  # Layer 2
            risk_pre_mortem=raw_json.get("risk_pre_mortem", []),  # Layer 4
            trigger=raw_json.get("trigger"),
            impact=raw_json.get("impact"),
            risks_structured=raw_json.get("risks_structured", []),
            alternatives=raw_json.get("alternatives", []),
            effort=raw_json.get("effort"),
            execution_plan=raw_json.get("execution_plan"),
        )
