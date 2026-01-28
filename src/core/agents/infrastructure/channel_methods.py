"""Agent Channel Communication Methods.

Additional methods for Agent base class to support channel coordination.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:

    class ChannelAction: ...

    class ChannelPolicy: ...

    class ChannelMessage: ...


async def send_to_agent(
    self,
    target_agent: str,
    action: Any,
    payload: Dict[str, Any],
    policy: Optional[Any] = None,
    trace_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send message to another agent through supervised channel.

    Args:
        target_agent: Target agent ID
        action: Channel action type
        payload: Message data
        policy: Governance policy (defaults to READ_ONLY)
        trace_id: Observability trace
        session_id: User session

    Returns:
        Delivery confirmation

    Raises:
        RuntimeError: If channel router not initialized
    """
    if not self.channel_router:
        raise RuntimeError(f"Channel router not initialized for agent {self.agent_id}")

    from src.core.coordination.policies import POLICY_READ_ONLY
    from src.core.kb.schemas import uid

    channel_policy = policy or POLICY_READ_ONLY

    # Create channel if needed
    channel = await self.channel_router.create_channel(
        from_agent=self.agent_id,
        to_agent=target_agent,
        policy=channel_policy,
        trace_id=trace_id or uid(),
        session_id=session_id or "agent_coordination",
    )

    # Send message
    result = await self.channel_router.send_message(
        channel_id=channel.channel_id, from_agent=self.agent_id, action=action, payload=payload
    )

    return result


async def on_channel_message(self, message: Any) -> Optional[Dict[str, Any]]:
    """
    Handle incoming channel message.

    Override in subclass to implement custom handling.

    Args:
        message: Incoming channel message

    Returns:
        Optional response payload
    """
    # Default: log and acknowledge
    print(f"📨 [{self.agent_id}] Received channel message from {message.from_agent}")
    print(f"   Action: {message.action.value}")
    print(f"   Payload: {message.payload}")

    return {"status": "acknowledged", "agent": self.agent_id}
