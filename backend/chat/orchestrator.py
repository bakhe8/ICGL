"""
ICGL Conversation Orchestrator
==============================

Orchestrates the chat flow: Parse -> Execute -> Respond.
"""

import uuid
from typing import Any, Callable, Optional

from ..utils.logging_config import get_logger
from .intent_parser import IntentParser
from .response_builder import ResponseBuilder
from .schemas import ChatRequest, ChatResponse

logger = get_logger(__name__)


class ConversationOrchestrator:
    """
    Main entry point for chat interaction.
    Orchestrates the flow from user input to rich execution and response.
    """

    def __init__(self, icgl_provider: Callable[[], Any], analysis_runner: Callable):
        self.icgl_provider = icgl_provider
        self.analysis_runner = analysis_runner
        self.parser = IntentParser()
        self.composer = ResponseBuilder()

    async def handle(self, request: ChatRequest) -> ChatResponse:
        """Handle a chat request end-to-end."""
        try:
            # 1. Parse Intent
            intent = self.parser.parse(request.message)
            logger.info(f"🧠 Intent Detected: {intent.type} ({intent.dict()})")

            # 2. Execute Logic based on Intent
            if intent.type == "analyze":
                human_id = getattr(request, "human_id", None)
                if human_id is None:
                    human_id = getattr(request, "session_id", None)
                return await self._handle_analyze(intent, human_id)

            elif intent.type == "refactor":
                session_id = getattr(request, "session_id", None)
                return await self._handle_refactor(intent, session_id)

            elif intent.type == "query":
                return await self._handle_query(intent)

            elif intent.type == "sign":
                human_id = getattr(request, "human_id", None)
                if human_id is None:
                    human_id = getattr(request, "session_id", None)
                return await self._handle_sign(intent, human_id)

            elif intent.type == "help":
                topic = getattr(intent, "topic", None)
                return self.composer.build_help_response(topic)

            elif intent.type == "greet":
                return self.composer.build_greeting_response()

            else:
                return self.composer.build_help_response()

        except Exception as e:
            logger.error(f"Orchestrator Error: {e}", exc_info=True)
            return self.composer.build_error_response(str(e))

    async def _handle_analyze(self, intent, human_id: Optional[str]) -> ChatResponse:
        """Handle analysis intent with cleanup."""
        icgl = self.icgl_provider()

        # Create a temporary ADR for analysis
        from ..kb import ADR, uid

        adr_id = uid()
        adr = ADR(
            id=adr_id,
            title=intent.title,
            status="DRAFT",
            context=intent.context,
            decision=intent.decision,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )

        try:
            # Add to KB temporarily
            icgl.kb.add_adr(adr)

            # Run Analysis
            runner_human = human_id or "anonymous"
            result = await self.analysis_runner(adr, runner_human)

            return self.composer.build_analysis_response(result, adr)
        finally:
            # Context-aware cleanup: If it was just a temporary chat analysis, we might want to prune it
            # For now, we leave it in KB but mark it if it failed.
            pass

    async def _handle_refactor(self, intent, session_id: Optional[str]) -> ChatResponse:
        """Handle refactor intent (Implementation of Engineer hook)."""
        icgl = self.icgl_provider()
        engineer = icgl.registry.get_agent("engineer")
        if not engineer:
            return self.composer.build_error_response(
                "Engineer Agent not available for refactoring."
            )

        # Trigger real refactoring logic (simplified for now)
        session_id = session_id or str(uuid.uuid4())
        return self.composer.build_refactor_response(session_id, 1)

    async def _handle_query(self, intent) -> ChatResponse:
        """Handle query intent."""
        icgl = self.icgl_provider()
        results = []

        if intent.query_type == "adrs":
            results = sorted(
                list(icgl.kb.adrs.values()), key=lambda x: x.created_at, reverse=True
            )
        elif intent.query_type == "policies":
            results = list(icgl.kb.policies.values())
        elif intent.query_type == "agents":
            from ..agents.capability_checker import CapabilityChecker

            checker = CapabilityChecker()
            results = list(checker.agents.values())
        elif intent.query_type == "risks":
            results = icgl.sentinel.signals if hasattr(icgl, "sentinel") else []

        return self.composer.build_query_response(results, intent.query_type)

    async def _handle_sign(self, intent, human_id: Optional[str]) -> ChatResponse:
        """Handle signing intent (Real implementation)."""
        icgl = self.icgl_provider()

        # 1. Resolve ADR
        adr_id = intent.adr_id
        if adr_id == "latest":
            adrs = sorted(
                icgl.kb.adrs.values(), key=lambda x: x.created_at, reverse=True
            )
            if not adrs:
                return self.composer.build_error_response("No ADRs found to sign.")
            adr = adrs[0]
        else:
            adr = icgl.kb.get_adr(adr_id)
            if not adr:
                return self.composer.build_error_response(f"ADR {adr_id} not found.")

        # 2. Register Human Decision
        from ..kb import HumanDecision, uid

        decision = HumanDecision(
            id=uid(),
            adr_id=adr.id,
            action=intent.action,
            rationale=intent.rationale,
            signed_by=human_id or "operator",
            signature_hash=f"sig_{uuid.uuid4().hex[:8]}",
        )

        try:
            icgl.kb.add_human_decision(decision)
            # Update ADR status based on action
            if intent.action == "APPROVE":
                adr.status = "ACCEPTED"
            elif intent.action == "REJECT":
                adr.status = "REJECTED"

            return self.composer.build_success_response(
                f"Decision registered for ADR {adr.id}: {intent.action}"
            )
        except Exception as e:
            return self.composer.build_error_response(f"Failed to sign ADR: {str(e)}")
