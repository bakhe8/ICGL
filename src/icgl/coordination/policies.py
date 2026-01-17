"""
Channel Policy Framework
-------------------------

Defines what actions are permitted in supervised agent channels.
"""

from dataclasses import dataclass
from typing import Set
from enum import Enum


class ChannelAction(Enum):
    """
    Actions that agents can perform through channels.
    
    Philosophy: Whitelist approach. Only explicitly allowed actions permitted.
    """
    # Safe read-only operations
    READ_KB = "read_kb"                    # Query knowledge base
    QUERY_SENTINEL = "query_sentinel"      # Ask sentinel for guidance
    SHARE_ANALYSIS = "share_analysis"      # Exchange analysis results
    
    # Coordination
    REQUEST_REVIEW = "request_review"      # Ask another agent to review
    PROPOSE_CHANGE = "propose_change"      # Suggest state modification
    REQUEST_APPROVAL = "request_approval"  # Ask for permission
    
    # FORBIDDEN (never allowed through channels):
    # MUTATE_KB - direct state changes
    # EXECUTE_DECISION - bypassing HDAL
    # MODIFY_POLICY - governance changes


@dataclass
class ChannelPolicy:
    """
    Governance policy for a communication channel.
    
    Defines:
    - What actions are permitted
    - Resource limits (messages, time)
    - Escalation requirements
    - Sentinel monitoring rules
    """
    policy_id: str
    name: str
    description: str
    
    # Permissions (whitelist)
    allowed_actions: Set[ChannelAction]
    can_read_kb: bool = False
    can_query_sentinel: bool = False
    can_propose: bool = False
    
    # Resource Constraints
    max_messages: int = 100           # Prevent infinite loops
    max_duration_seconds: int = 60    # Auto-close timeout
    
    # Governance
    requires_human_approval: bool = False  # Escalate proposals to HDAL?
    requires_gbe_validation: bool = True   # Always validate through GBE
    
    # Sentinel Integration
    alert_on_violations: bool = True
    block_on_critical: bool = True
    auto_close_on_violation: bool = False
    
    def is_action_allowed(self, action: ChannelAction) -> bool:
        """Check if action is permitted by this policy"""
        return action in self.allowed_actions


# ============================================================================
# Predefined Policies
# ============================================================================

POLICY_READ_ONLY = ChannelPolicy(
    policy_id="policy_readonly",
    name="Read-Only Coordination",
    description="Agents can share analysis and query data, but not propose changes",
    allowed_actions={
        ChannelAction.SHARE_ANALYSIS,
        ChannelAction.READ_KB,
        ChannelAction.QUERY_SENTINEL
    },
    can_read_kb=True,
    can_query_sentinel=True,
    can_propose=False,
    max_messages=50,
    max_duration_seconds=30,
    requires_human_approval=False,
    alert_on_violations=True
)

POLICY_COLLABORATIVE = ChannelPolicy(
    policy_id="policy_collaborative",
    name="Collaborative Analysis",
    description="Agents can coordinate and propose changes (with human approval)",
    allowed_actions={
        ChannelAction.SHARE_ANALYSIS,
        ChannelAction.READ_KB,
        ChannelAction.QUERY_SENTINEL,
        ChannelAction.REQUEST_REVIEW,
        ChannelAction.PROPOSE_CHANGE,
        ChannelAction.REQUEST_APPROVAL
    },
    can_read_kb=True,
    can_query_sentinel=True,
    can_propose=True,
    max_messages=100,
    max_duration_seconds=120,
    requires_human_approval=True,  # Proposals need HDAL sign-off
    requires_gbe_validation=True,
    alert_on_violations=True,
    block_on_critical=True,
    auto_close_on_violation=False
)

POLICY_RESTRICTED = ChannelPolicy(
    policy_id="policy_restricted",
    name="Minimal Coordination",
    description="Very limited channel for simple information exchange",
    allowed_actions={ChannelAction.SHARE_ANALYSIS},
    can_read_kb=False,
    can_query_sentinel=False,
    can_propose=False,
    max_messages=10,
    max_duration_seconds=15,
    requires_human_approval=False,
    alert_on_violations=True,
    block_on_critical=True,
    auto_close_on_violation=True  # Immediately close on any violation
)

# List of all static policies
ALL_POLICIES = [
    POLICY_READ_ONLY,
    POLICY_COLLABORATIVE,
    POLICY_RESTRICTED
]
