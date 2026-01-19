"""
ICGL Chat Package
=================

Conversational interface components.
"""

from .api_models import (
    ChatRequest, ChatResponse, ChatMessage, MessageBlock,
    ChatContext, Intent
)
from .intent_parser import IntentParser
from .response_builder import ResponseBuilder

__all__ = [
    "ChatRequest", "ChatResponse", "ChatMessage", "MessageBlock",
    "ChatContext", "Intent",
    "IntentParser", "ResponseBuilder"
]
