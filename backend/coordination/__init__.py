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
    def to_dict(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "policy": getattr(self.policy, "name", str(self.policy)),
            "trace_id": self.trace_id,
            "session_id": self.session_id,
        }


class DirectChannelRouter:
    """No-op router to satisfy imports; does not persist or deliver messages."""

    def __init__(self, icgl_provider=None):
        self.icgl_provider = icgl_provider
        self._channels = {}

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

    def get_active_channels(self) -> List[Channel]:
        return list(self._channels.values())

    async def terminate_channel(self, channel_id: str, reason: str = "user", terminated_by: str = "system") -> dict:
        if channel_id in self._channels:
            del self._channels[channel_id]
            return {"status": "terminated", "channel_id": channel_id, "reason": reason, "by": terminated_by}
        return {"status": "not_found", "channel_id": channel_id}

    def get_stats(self) -> dict:
        return {"active_channels": len(self._channels)}

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        return self._channels.get(channel_id)

    async def _build_policy_context(self, *args, **kwargs) -> dict:
        # minimal async context builder
        return {"context": "policy_context"}


# --- Policies stub ---
class ChannelPolicy:
    def __init__(self, name: str):
        self.name = name


POLICY_READ_ONLY = ChannelPolicy("read_only")


# --- Advanced policies stub (for api/server imports) ---
def get_policy_registry() -> List[Any]:
    return [POLICY_READ_ONLY]
