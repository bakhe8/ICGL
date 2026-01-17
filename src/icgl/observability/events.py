"""
Observability Event Models
---------------------------

Defines taxonomy and schema for all observable system events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class EventType(Enum):
    """Taxonomy of observable events in ICGL"""
    
    # Agent Lifecycle
    AGENT_INVOKED = "agent.invoked"
    AGENT_RESPONDED = "agent.responded"
    AGENT_FAILED = "agent.failed"
    
    # LLM Operations
    LLM_CALLED = "llm.called"
    LLM_RESPONDED = "llm.responded"
    LLM_FAILED = "llm.failed"
    
    # Knowledge Base
    KB_READ = "kb.read"
    KB_WRITE = "kb.write"
    
    # Policy Engine
    POLICY_CHECKED = "policy.checked"
    POLICY_VIOLATED = "policy.violated"
    
    # Sentinel
    SENTINEL_SCANNED = "sentinel.scanned"
    SENTINEL_ALERT = "sentinel.alert"
    
    # Human Decision Layer
    HDAL_REQUESTED = "hdal.requested"
    HDAL_SIGNED = "hdal.signed"
    
    # Governance Binding
    GBE_BIND = "gbe.bind"
    GBE_UNBIND = "gbe.unbind"
    
    # Future: Channel Events (Phase 2)
    CHANNEL_CREATED = "channel.created"
    CHANNEL_MESSAGE = "channel.message"
    CHANNEL_CLOSED = "channel.closed"


@dataclass
class ObservabilityEvent:
    """
    Immutable record of a single system event.
    
    Philosophy: Capture everything. Storage is cheap, missing data is expensive.
    """
    
    # === Identity ===
    event_id: str  # Unique identifier for this event
    event_type: EventType  # Type of event from taxonomy
    timestamp: datetime  # When did this happen
    
    # === Tracing (Critical for replay) ===
    trace_id: str  # Groups all events for one decision/request
    span_id: str  # Identifies this specific operation
    parent_span_id: Optional[str] = None  # Parent operation (for nesting)
    session_id: str = "unknown"  # User session
    adr_id: Optional[str] = None  # Related ADR if any
    
    # === Actor ===
    actor_type: str = "system"  # "agent", "human", "system"
    actor_id: str = "unknown"  # e.g., "architect_agent", "bakheet"
    
    # === Action ===
    action: str = ""  # Verb: "analyze", "check_policy", "query_kb"
    target: Optional[str] = None  # What was acted upon
    
    # === Data ===
    input_payload: Optional[Dict[str, Any]] = None  # Input data
    output_payload: Optional[Dict[str, Any]] = None  # Output data
    
    # === Outcome ===
    status: str = "pending"  # "success", "failure", "pending"
    error_message: Optional[str] = None  # If failed, why
    
    # === Performance ===
    duration_ms: Optional[int] = None  # How long did it take
    
    # === Metadata ===
    tags: Dict[str, str] = field(default_factory=dict)  # Extensible metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "session_id": self.session_id,
            "adr_id": self.adr_id,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "action": self.action,
            "target": self.target,
            "input_payload": self.input_payload,
            "output_payload": self.output_payload,
            "status": self.status,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservabilityEvent":
        """Create from dictionary"""
        data = data.copy()
        data["event_type"] = EventType(data["event_type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
