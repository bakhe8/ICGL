"""
ICGL Chat Package
=================

Conversational interface components.
"""

from .api_models import (
    ChatRequest, ChatResponse, ChatMessage, MessageBlock,
    ChatContext, Intent
)
__all__ = [
    "ChatRequest", "ChatResponse", "ChatMessage", "MessageBlock",
    "ChatContext", "Intent"
]
