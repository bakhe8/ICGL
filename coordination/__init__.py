"""
ICGL Coordination Subsystem
============================

Supervised agent-to-agent communication through governed channels.

Phase 2: Direct Channel Router for swarm intelligence under ICGL sovereignty.
"""

from coordination.policies import (
    ChannelAction,
    ChannelPolicy,
    POLICY_READ_ONLY,
    POLICY_COLLABORATIVE,
)
from coordination.channel import (
    ChannelStatus,
    ChannelMessage,
    DirectChannel,
)
from coordination.router import DirectChannelRouter
from coordination.idcp import CoordinationOrchestrator

__all__ = [
    "ChannelAction",
    "ChannelPolicy",
    "POLICY_READ_ONLY",
    "POLICY_COLLABORATIVE",
    "ChannelStatus",
    "ChannelMessage",
    "DirectChannel",
    "DirectChannelRouter",
]
