"""
Consensus AI — Architect Agent
===============================

Analyzes structural implications of decisions.
Focuses on cohesion, coupling, and long-term maintainability.
Uses Real LLM (via LLMClient) for intelligence, governed by strict JSON schemas.
"""

from typing import Any, Dict, Optional

from ..core.context import ContextBuilder  # Cycle 8
from ..llm.client import LLMClient, LLMConfig
from ..llm.prompts import (
    ARCHITECT_SYSTEM_PROMPT,
    JSONParser,
    build_architect_user_prompt,
)
from .base import Agent, AgentResult, AgentRole, Problem


class ArchitectAgent(Agent):
    """
    Architectural analysis agent.
    Checks for:
    - Coupling/Cohesion
    - System boundaries
    - Strategic optionality (P-CORE-01)
    """

    def __init__(self, llm_provider=None):
        # We ignore passed provider for now and use our robust LLMClient
        super().__init__(
            agent_id="agent-architect",
            role=AgentRole.ARCHITECT,
            llm_provider=llm_provider,
        )
        self.llm_client = LLMClient()
        self.context_builder = ContextBuilder(".")

    def get_system_prompt(self) -> str:
        """
        Injects the Map into the default Architect Prompt.
        """
        try:
            repo_map = self.context_builder.generate_map(max_depth=3)
        except Exception:
            repo_map = "(Map generation failed)"

        return f"{ARCHITECT_SYSTEM_PROMPT}\n\n📡 REPOSITORY MAP:\n{repo_map}"

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Runs the LLM-based architectural analysis.
        Strictly governed:
        - Timeout enforced
        - JSON only
        - No side effects
        """

        # 1. Build Context (Read-Only)
        context = problem.context
        decision = problem.metadata.get("decision", "N/A")

        # 1.1 Inject Technical Intent from Secretary (Cycle 14)
        if hasattr(self, "_pending_intent") and self._pending_intent:
            print(
                f"   🔗 [Architect] Using Technical Intent from Native Layer: {self._pending_intent[:40]}..."
            )
            context = (
                f"STRICT TECHNICAL INTENT (FROM SECRETARY): {self._pending_intent}\n\n"
                + context
            )
            # Clear it after consumption
            self._pending_intent = None

        # 1.5 Recall Institutional Memory (Consult the Steward)
        steward_result = await self.consult_peer(
            AgentRole.STEWARD,
            title=f"Architectural Context: {problem.title}",
            context=context,
            kb=kb,
        )
        if steward_result and steward_result.confidence > 0.5:
            print("   🏛️ [Architect] Consulted Knowledge Steward for history.")
            context += f"\n\nINSTITUTIONAL MEMORY (From Knowledge Steward):\n{steward_result.analysis}\n"
            if steward_result.references:
                context += "Historical References:\n"
                for ref in steward_result.references:
                    context += f"- {ref}\n"

        # 2. Construct Prompt
        user_prompt = build_architect_user_prompt(
            title=problem.title, context=context, decision=decision
        )

        # 3. Configure Safe Execution
        config = LLMConfig(
            model="gpt-4-turbo-preview",
            temperature=0.0,  # Deterministic
            timeout=45.0,  # Explicit timeout
            max_tokens=2000,
            json_mode=True,
        )

        # 4. Execute LLM Call (Exceptions caught by Base Class Shield)
        if not self.llm_client.api_key:
            return self._fallback_result(
                "Missing OPENAI_API_KEY. Cannot run real agent."
            )

        raw_json, usage = await self.llm_client.generate_json(
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            config=config,
        )

        # Update Budget Tracking
        current_tokens = problem.metadata.get("total_tokens", 0)
        problem.metadata["total_tokens"] = current_tokens + usage.get("total_tokens", 0)
        problem.metadata["last_agent_tokens"] = usage.get("total_tokens", 0)

        # 5. Parse & Validate
        parsed = JSONParser.parse_architect_output(raw_json)

        # 6. Convert to Schema Objects
        from ..kb.schemas import FileChange
        from .base import IntentContract

        intent = None
        if parsed.intent_contract:
            ic = parsed.intent_contract
            intent = IntentContract(
                goal=ic.get("goal", ""),
                risk_level=ic.get("risk_level", "medium"),
                allowed_files=ic.get("allowed_files", []),
                forbidden_zones=ic.get("forbidden_zones", []),
                constraints=ic.get("constraints", []),
                success_criteria=ic.get("success_criteria", []),
                micro_examples=ic.get("micro_examples", []),
            )

        file_changes_objs = []
        if hasattr(parsed, "file_changes"):
            for fc in parsed.file_changes:
                file_changes_objs.append(
                    FileChange(
                        path=fc["path"],
                        content=fc["content"],
                        action=fc.get("action", "CREATE"),
                    )
                )

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=parsed.analysis,
            recommendations=parsed.recommendations,
            concerns=parsed.risks,
            confidence=parsed.confidence_score,
            file_changes=file_changes_objs,
            clarity_needed=parsed.clarity_needed,
            clarity_question=parsed.clarity_question,
            trigger=parsed.trigger,
            impact=parsed.impact,
            risks_structured=parsed.risks_structured,
            alternatives=parsed.alternatives,
            effort=parsed.effort,
            execution_plan=parsed.execution_plan,
            # Layer 1: The Sovereign Intent
            intent=intent,
            understanding={
                "interpretation": f"Architecture Goal: {intent.goal if intent else 'N/A'}",
                "confidence": parsed.confidence_score,
            }
            if intent
            else None,
        )

    async def on_channel_message(self, message: Any) -> Optional[Dict[str, Any]]:
        """
        Receive Technical Intent from Secretary (Cycle 14).
        Store it in temporary memory for the next analysis cycle.
        """
        if message.action == "PROPOSE_INTENT":
            payload = message.payload
            technical_intent = payload.get("technical_intent")
            print(
                f"   🏛️ [Architect] Received Intent from Secretary: {technical_intent[:50]}..."
            )

            # Store for the immediate next analysis
            # We use a simple instance variable for this session
            self._pending_intent = technical_intent
            return {"status": "intent_received"}

        return await super().on_channel_message(message)
