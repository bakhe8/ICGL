"""
Direct Channel
--------------

Supervised communication path between agents with full governance.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from .policies import ChannelAction, ChannelPolicy


class ChannelStatus(Enum):
    """Lifecycle status of a channel"""
    PENDING = "pending"        # Awaiting GBE approval
    ACTIVE = "active"          # Open for communication
    PAUSED = "paused"          # Temporarily suspended by human
    CLOSED = "closed"          # Normally terminated
    VIOLATED = "violated"      # Policy violation detected
    EMERGENCY_CLOSED = "emergency_closed"  # Human emergency shutdown


@dataclass
class ChannelMessage:
    """
    A single message exchanged through a channel.
    
    All messages are logged to Observability Ledger.
    """
    message_id: str
    from_agent: str
    to_agent: str
    action: ChannelAction
    payload: Dict[str, Any]
    timestamp: datetime
    trace_id: str  # Links to observability trace
    
    # Response tracking
    response_to: Optional[str] = None  # message_id being responded to
    requires_response: bool = False


@dataclass
class DirectChannel:
    """
    Supervised communication channel between agents.
    
    Key Principles:
    - Every channel has a governing policy
    - All messages logged to Observability Ledger
    - Sentinel monitors for violations
    - Human can terminate anytime
    - GBE validates before activation
    """
    
    # Identity
    channel_id: str
    from_agent: str
    to_agent: str
    
    # Governance
    policy: ChannelPolicy
    status: ChannelStatus
    
    # Tracing (for observability)
    trace_id: str
    session_id: str
    
    # Optional fields with defaults
    direction: str = "bidirectional"  # or "unidirectional"
    adr_id: Optional[str] = None
    
    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)

    activated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    closed_reason: Optional[str] = None
    closed_by: str = "system"  # "system", "human", "sentinel"
    
    # Messages
    messages: List[ChannelMessage] = field(default_factory=list)
    message_count: int = 0
    
    # Violations
    violations: List[Dict[str, Any]] = field(default_factory=list)
    violation_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def can_send_message(self, action: ChannelAction) -> tuple[bool, Optional[str]]:
        """
        Check if a message with given action can be sent.
        
        Returns:
            (allowed, error_reason)
        """
        # Status check
        if self.status != ChannelStatus.ACTIVE:
            return False, f"Channel is {self.status.value}, not active"
        
        # Policy check
        if not self.policy.is_action_allowed(action):
            return False, f"Action '{action.value}' not allowed by policy '{self.policy.name}'"
        
        # Message limit check
        if self.message_count >= self.policy.max_messages:
            return False, f"Message limit reached ({self.policy.max_messages})"
        
        # Duration check
        if self.activated_at:
            duration = (datetime.utcnow() - self.activated_at).total_seconds()
            if duration > self.policy.max_duration_seconds:
                return False, f"Channel timeout ({self.policy.max_duration_seconds}s exceeded)"
        
        return True, None
    
    def add_message(self, message: ChannelMessage) -> None:
        """Add message to channel history"""
        self.messages.append(message)
        self.message_count += 1
    
    def add_violation(
        self,
        reason: str,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record policy violation"""
        violation = {
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "severity": severity,
            "details": details or {}
        }
        self.violations.append(violation)
        self.violation_count += 1
        
        # Auto-close on critical if policy requires
        if severity == "critical" and self.policy.auto_close_on_violation:
            self.status = ChannelStatus.VIOLATED
    
    def activate(self) -> None:
        """Activate channel (called after GBE approval)"""
        self.status = ChannelStatus.ACTIVE
        self.activated_at = datetime.utcnow()
    
    def pause(self, reason: str) -> None:
        """Temporarily pause channel"""
        self.status = ChannelStatus.PAUSED
        self.metadata["pause_reason"] = reason
        self.metadata["paused_at"] = datetime.utcnow().isoformat()
    
    def resume(self) -> None:
        """Resume paused channel"""
        if self.status == ChannelStatus.PAUSED:
            self.status = ChannelStatus.ACTIVE
            self.metadata["resumed_at"] = datetime.utcnow().isoformat()
    
    def close(self, reason: str, closed_by: str = "system") -> None:
        """Close channel"""
        self.status = ChannelStatus.CLOSED
        self.closed_at = datetime.utcnow()
        self.closed_reason = reason
        self.closed_by = closed_by
    
    def emergency_close(self, reason: str) -> None:
        """Emergency human-initiated closure"""
        self.status = ChannelStatus.EMERGENCY_CLOSED
        self.closed_at = datetime.utcnow()
        self.closed_reason = reason
        self.closed_by = "human"
    
    def get_duration(self) -> Optional[float]:
        """Get channel duration in seconds"""
        if not self.activated_at:
            return None
        end_time = self.closed_at or datetime.utcnow()
        return (end_time - self.activated_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API/logging"""
        return {
            "channel_id": self.channel_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "direction": self.direction,
            "policy": {
                "id": self.policy.policy_id,
                "name": self.policy.name
            },
            "status": self.status.value,
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "adr_id": self.adr_id,
            "created_at": self.created_at.isoformat(),
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "closed_reason": self.closed_reason,
            "closed_by": self.closed_by,
            "message_count": self.message_count,
            "violation_count": self.violation_count,
            "duration_seconds": self.get_duration(),
            "metadata": self.metadata
        }
