"""
Advanced Channel Policies
--------------------------

Conditional and context-aware policies for sophisticated channel governance.

Features:
- Time-based policies (business hours, maintenance windows)
- Agent-history-based policies (trust scores, violation counts)
- System-state-based policies (load, active channels)
- Fallback mechanisms
"""

from dataclasses import dataclass, field
from typing import Set, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from .policies import ChannelPolicy, ChannelAction


class ConditionOperator(Enum):
    """Operators for policy conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    IN_RANGE = "in_range"
    NOT_IN_RANGE = "not_in_range"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"


@dataclass
class PolicyCondition:
    """
    Condition that must be met for a policy to apply.
    
    Conditions are evaluated against a runtime context dictionary.
    Multiple conditions can be combined with AND logic.
    """
    type: str  # Context key to evaluate (e.g., "hour", "violation_count_24h")
    operator: ConditionOperator
    value: Any  # Expected value or range
    description: str = ""
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if this condition is met.
        
        Args:
            context: Runtime context with current system state
            
        Returns:
            True if condition is met, False otherwise
        """
        actual = context.get(self.type)
        
        if actual is None:
            return False
        
        if self.operator == ConditionOperator.EQUALS:
            return actual == self.value
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return actual != self.value
        elif self.operator == ConditionOperator.GREATER_THAN:
            return actual > self.value
        elif self.operator == ConditionOperator.LESS_THAN:
            return actual < self.value
        elif self.operator == ConditionOperator.GREATER_OR_EQUAL:
            return actual >= self.value
        elif self.operator == ConditionOperator.LESS_OR_EQUAL:
            return actual <= self.value
        elif self.operator == ConditionOperator.IN_RANGE:
            if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                return False
            return self.value[0] <= actual <= self.value[1]
        elif self.operator == ConditionOperator.NOT_IN_RANGE:
            if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                return False
            return not (self.value[0] <= actual <= self.value[1])
        elif self.operator == ConditionOperator.CONTAINS:
            return self.value in actual
        elif self.operator == ConditionOperator.NOT_CONTAINS:
            return self.value not in actual
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "type": self.type,
            "operator": self.operator.value,
            "value": self.value,
            "description": self.description
        }


@dataclass
class ConditionalPolicy(ChannelPolicy):
    """
    Policy that adapts based on runtime conditions.
    
    If all conditions are met, this policy is used.
    Otherwise, falls back to the fallback_policy.
    """
    conditions: List[PolicyCondition] = field(default_factory=list)
    fallback_policy: Optional[ChannelPolicy] = None
    evaluation_strategy: str = "ALL"  # "ALL" or "ANY"
    
    def evaluate(self, context: Dict[str, Any]) -> ChannelPolicy:
        """
        Evaluate which policy should be active.
        
        Args:
            context: Runtime context
            
        Returns:
            Active policy (self or fallback)
        """
        if not self.conditions:
            return self
        
        # Evaluate all conditions
        results = [cond.evaluate(context) for cond in self.conditions]
        
        # Determine if conditions are met
        if self.evaluation_strategy == "ALL":
            conditions_met = all(results)
        else:  # "ANY"
            conditions_met = any(results)
        
        if conditions_met:
            return self
        
        return self.fallback_policy if self.fallback_policy else self
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        base = super().to_dict()
        base.update({
            "type": "conditional",
            "conditions": [c.to_dict() for c in self.conditions],
            "fallback_policy": self.fallback_policy.name if self.fallback_policy else None,
            "evaluation_strategy": self.evaluation_strategy
        })
        return base


# =============================================================================
# Pre-Defined Conditional Policies
# =============================================================================

# Import base policies for fallback
from .policies import POLICY_READ_ONLY, POLICY_COLLABORATIVE, POLICY_RESTRICTED

# Business Hours Policy
POLICY_BUSINESS_HOURS = ConditionalPolicy(
    policy_id="policy_business_hours",
    name="business_hours_collaborative",
    description="Full collaboration during business hours (9 AM - 5 PM, Mon-Fri), read-only otherwise",
    allowed_actions={
        ChannelAction.READ_KB,
        ChannelAction.QUERY_SENTINEL,
        ChannelAction.SHARE_ANALYSIS,
        ChannelAction.REQUEST_REVIEW,
        ChannelAction.PROPOSE_CHANGE,
        ChannelAction.REQUEST_APPROVAL
    },
    conditions=[
        PolicyCondition(
            type="hour",
            operator=ConditionOperator.IN_RANGE,
            value=(9, 17),
            description="Between 9 AM and 5 PM"
        ),
        PolicyCondition(
            type="day_of_week",
            operator=ConditionOperator.IN_RANGE,
            value=(0, 4),
            description="Monday through Friday"
        )
    ],
    fallback_policy=POLICY_READ_ONLY,
    max_messages=100,
    max_duration_seconds=300,
    requires_human_approval=False,
    alert_on_violations=True,
    evaluation_strategy="ALL"
)

# Trusted Agent Policy
POLICY_TRUSTED_AGENT = ConditionalPolicy(
    policy_id="policy_trusted_agent",
    name="trusted_agent",
    description="Extended permissions for agents with good track record",
    allowed_actions={
        ChannelAction.READ_KB,
        ChannelAction.QUERY_SENTINEL,
        ChannelAction.SHARE_ANALYSIS,
        ChannelAction.REQUEST_REVIEW,
        ChannelAction.PROPOSE_CHANGE,
        ChannelAction.REQUEST_APPROVAL
    },
    conditions=[
        PolicyCondition(
            type="violation_count_24h",
            operator=ConditionOperator.LESS_THAN,
            value=2,
            description="Less than 2 violations in last 24 hours"
        ),
        PolicyCondition(
            type="success_rate_7d",
            operator=ConditionOperator.GREATER_OR_EQUAL,
            value=0.85,
            description="At least 85% success rate in last 7 days"
        ),
        PolicyCondition(
            type="total_channels_created",
            operator=ConditionOperator.GREATER_THAN,
            value=5,
            description="Has created at least 5 channels (experienced)"
        )
    ],
    fallback_policy=POLICY_RESTRICTED,
    max_messages=150,
    max_duration_seconds=600,
    requires_human_approval=False,
    alert_on_violations=True,
    evaluation_strategy="ALL"
)

# Low Load Policy
POLICY_LOW_SYSTEM_LOAD = ConditionalPolicy(
    policy_id="policy_low_load",
    name="low_load_permissive",
    description="More permissive when system load is low",
    allowed_actions={
        ChannelAction.READ_KB,
        ChannelAction.QUERY_SENTINEL,
        ChannelAction.SHARE_ANALYSIS,
        ChannelAction.REQUEST_REVIEW,
        ChannelAction.PROPOSE_CHANGE
    },
    conditions=[
        PolicyCondition(
            type="active_channels",
            operator=ConditionOperator.LESS_THAN,
            value=10,
            description="Fewer than 10 active channels"
        ),
        PolicyCondition(
            type="system_load_percent",
            operator=ConditionOperator.LESS_THAN,
            value=50,
            description="System load below 50%"
        )
    ],
    fallback_policy=POLICY_READ_ONLY,
    max_messages=200,
    max_duration_seconds=900,
    requires_human_approval=False,
    alert_on_violations=False,
    evaluation_strategy="ALL"
)

# Emergency Restrictive Policy
POLICY_EMERGENCY_MODE = ConditionalPolicy(
    policy_id="policy_emergency",
    name="emergency_restrictive",
    description="Highly restrictive during emergencies or high violation periods",
    allowed_actions={
        ChannelAction.READ_KB,
        ChannelAction.QUERY_SENTINEL
    },
    conditions=[
        PolicyCondition(
            type="system_violations_1h",
            operator=ConditionOperator.GREATER_THAN,
            value=20,
            description="More than 20 system-wide violations in last hour"
        )
    ],
    fallback_policy=POLICY_COLLABORATIVE,
    max_messages=10,
    max_duration_seconds=60,
    requires_human_approval=True,
    alert_on_violations=True,
    evaluation_strategy="ANY"  # Trigger on any high-risk condition
)


# All available conditional policies
ALL_CONDITIONAL_POLICIES = [
    POLICY_BUSINESS_HOURS,
    POLICY_TRUSTED_AGENT,
    POLICY_LOW_SYSTEM_LOAD,
    POLICY_EMERGENCY_MODE
]


# =============================================================================
# Policy Registry
# =============================================================================

class PolicyRegistry:
    """Registry for all policies (static and conditional)"""
    
    def __init__(self):
        from .policies import ALL_POLICIES
        self.policies: Dict[str, ChannelPolicy] = {}
        
        # Register static policies
        for policy in ALL_POLICIES:
            self.policies[policy.name] = policy
        
        # Register conditional policies
        for policy in ALL_CONDITIONAL_POLICIES:
            self.policies[policy.name] = policy
    
    def get(self, name: str) -> Optional[ChannelPolicy]:
        """Get policy by name"""
        return self.policies.get(name)
    
    def list_all(self) -> List[ChannelPolicy]:
        """List all policies"""
        return list(self.policies.values())
    
    def list_conditional(self) -> List[ConditionalPolicy]:
        """List only conditional policies"""
        return [p for p in self.policies.values() if isinstance(p, ConditionalPolicy)]
    
    def register(self, policy: ChannelPolicy):
        """Register a new policy"""
        self.policies[policy.name] = policy
    
    def unregister(self, name: str):
        """Unregister a policy"""
        self.policies.pop(name, None)


# Global registry instance
_registry = PolicyRegistry()

def get_policy_registry() -> PolicyRegistry:
    """Get global policy registry"""
    return _registry
