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

            else:
                return self.composer.build_help_response()

        except Exception as e:
            logger.error(f"Orchestrator Error: {e}", exc_info=True)
            return self.composer.build_error_response(str(e))

    async def _handle_analyze(self, intent, human_id: Optional[str]) -> ChatResponse:
        """Handle analysis intent."""
        icgl = self.icgl_provider()

        # Create a temporary ADR for analysis
        from ..kb import ADR, uid

        adr = ADR(
            id=uid(),
            title=intent.title,
            status="DRAFT",
            context=intent.context,
            decision=intent.decision,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )

        # Add to KB temporarily
        icgl.kb.add_adr(adr)

        # Run Analysis (ensure human_id is a string)
        runner_human = human_id or "anonymous"
        result = await self.analysis_runner(adr, runner_human)

        return self.composer.build_analysis_response(result, adr)

    async def _handle_refactor(self, intent, session_id: Optional[str]) -> ChatResponse:
        """Handle refactor intent."""
        # Mock implementation for now - fully implementing requires Engineer Agent hookup
        session_id = session_id or str(uuid.uuid4())
        return self.composer.build_refactor_response(session_id, 42)

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
        elif intent.query_type == "risks":
            # Mock risk query
            results = []

        return self.composer.build_query_response(results, intent.query_type)

    async def _handle_sign(self, intent, human_id: Optional[str]) -> ChatResponse:
        """Handle signing intent."""
        # For signing via chat, we usually need more context or a specific pending ADR
        # This is a simplified handler
        return self.composer.build_error_response(
            "Signing via chat requires an active analysis context. Please use the 'Sign' button in an analysis result."
        )
