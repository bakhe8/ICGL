from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Message:
    """
    Standard envelope for inter-agent communication.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = "general"
    sender: str = "system"
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None  # For security mandate


class EventBus:
    """
    Central Nervous System for Agent Communication.
    Supports Pub/Sub pattern with topic filtering.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {}  # Dict[str, List[Callable]]
            cls._instance.wildcard_subscribers = []  # List[Callable]
            cls._instance.history = []  # Brief history buffer
            cls._instance.lock = asyncio.Lock()
        return cls._instance

    def subscribe(self, topic: str, handler: Callable[[Message], Any]):
        """Register a handler for a specific topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)
        print(f"📡 [Bus] Subscribed to '{topic}'")

    def subscribe_all(self, handler: Callable[[Message], Any]):
        """Register a handler for ALL topics."""
        self.wildcard_subscribers.append(handler)
        print("📡 [Bus] Wildcard Subscribed (ALL)")

    async def publish(
        self,
        topic: str,
        sender: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ):
        """Broadcast a message to all subscribers of the topic."""
        msg = Message(topic=topic, sender=sender, payload=payload, priority=priority)

        # Log to history
        self.history.append(msg)
        if len(self.history) > 1000:
            self.history.pop(0)

        # 1. Dispatch to Specific Topic Handlers
        if topic in self.subscribers:
            handlers = self.subscribers[topic]
            print(
                f"📨 [Bus] Dispatching '{topic}' from {sender} to {len(handlers)} handlers..."
            )
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(msg)
                    else:
                        handler(msg)
                except Exception as e:
                    print(f"❌ [Bus] Handler failed for {topic}: {e}")
        else:
            print(f"⚠️ [Bus] No subscribers for '{topic}'")

        # 2. Dispatch to Wildcard (Global) Handlers
        if self.wildcard_subscribers:
            for handler in self.wildcard_subscribers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(msg)
                    else:
                        handler(msg)
                except Exception as e:
                    print(f"❌ [Bus] Wildcard Handler failed: {e}")

    def get_history(self, limit: int = 10) -> List[Message]:
        return self.history[-limit:]


# Global accessor
_bus = EventBus()


def get_bus() -> EventBus:
    return _bus
