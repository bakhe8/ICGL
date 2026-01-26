"""
Core domain (canonical).

Contains shared infrastructure: context builder, runtime guard, observability hooks,
LLM interface, event bus, and resilience helpers.
"""

from .bus import EventBus as Bus, get_bus
from .context import ContextBuilder
from .llm import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    MockProvider,
    OpenAIProvider,
)
from .observability import SystemObserver
from .resilience import FailureContainer
from .runtime_guard import RuntimeIntegrityGuard, RuntimeIntegrityError

__all__ = [
    "Bus",
    "get_bus",
    "ContextBuilder",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "MockProvider",
    "OpenAIProvider",
    "SystemObserver",
    "FailureContainer",
    "RuntimeIntegrityGuard",
    "RuntimeIntegrityError",
]
