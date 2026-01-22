"""
Compatibility stubs for coordination layer.

The original project referenced backend.coordination.* modules. To keep the
engine running, we provide minimal placeholders that satisfy imports without
changing existing agent logic. Replace with real implementations when needed.
"""

from typing import Any, List, Optional
from dataclasses import dataclass


# --- Channel primitives (minimal) ---
@dataclass
class ChannelMessage:
    channel_id: str
    from_agent: str
    to_agent: str
    action: Any
    payload: dict


@dataclass
class Channel:
    channel_id: str
    from_agent: str
    to_agent: str
    policy: Any
    trace_id: str
    session_id: str


class DirectChannelRouter:
    """No-op router to satisfy imports; does not persist or deliver messages."""

    def __init__(self, icgl_provider=None):
        self.icgl_provider = icgl_provider

    async def create_channel(self, from_agent: str, to_agent: str, policy: Any, trace_id: str, session_id: str) -> Channel:
        return Channel(
            channel_id=f"{from_agent}->{to_agent}",
            from_agent=from_agent,
            to_agent=to_agent,
            policy=policy,
            trace_id=trace_id,
            session_id=session_id,
        )

    async def send_message(self, channel_id: str, from_agent: str, action: Any, payload: dict) -> dict:
        # No-op delivery; just echo back for now.
        return {"status": "sent", "channel_id": channel_id, "from": from_agent, "action": getattr(action, 'value', str(action)), "payload": payload}


# --- Policies stub ---
class ChannelPolicy:
    def __init__(self, name: str):
        self.name = name


POLICY_READ_ONLY = ChannelPolicy("read_only")


# --- Advanced policies stub (for api/server imports) ---
def get_policy_registry() -> List[Any]:
    return [POLICY_READ_ONLY]
