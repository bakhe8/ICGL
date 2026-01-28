"""
ICGL Core — Secure Message Bus
==============================

"The Central Nervous System."
Handles asynchronous communication between agents and components.
"""

import asyncio
from typing import Any, Callable, Dict, List


class MessageBus:
    """
    Simple Pub/Sub Message Bus for ICGL Agents.
    In production, this would bridge to a distributed system like Redis or NATS.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    async def publish(self, topic: str, from_agent: str, payload: Dict[str, Any]):
        """Publishes a message to all subscribers of a topic."""
        if topic in self._subscribers:
            tasks = [handler(payload) for handler in self._subscribers[topic]]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def subscribe(self, topic: str, handler: Callable):
        """Subscribes a handler to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)


# Singleton Pattern for Global Access
_bus = None


def get_bus() -> MessageBus:
    """Gets the global message bus singleton."""
    global _bus
    if _bus is None:
        _bus = MessageBus()
    return _bus
