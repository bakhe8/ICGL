from . import POLICY_READ_ONLY, ChannelPolicy, PolicyAction
from typing import List, Any, Optional


class ConditionalPolicy(ChannelPolicy):
    def __init__(self, name: str, conditions: Optional[List[Any]] = None):
        super().__init__(name)
        self.conditions: List[Any] = conditions or []
        self.allowed_actions: List[PolicyAction] = [PolicyAction("READ"), PolicyAction("NOTIFY")]
        self.max_messages = 10
        self.max_duration_seconds = 3600
        self.description = f"Conditional policy {name}"
        self.requires_human_approval = False
        self.alert_on_violations = True
        self.fallback_policy = None
        self.evaluation_strategy = "all"
    
    def evaluate(self, context: dict) -> bool:
        # Simple stub: return True if no conditions, else evaluate all
        if not self.conditions:
            return True
        return all(getattr(c, "evaluate", lambda ctx: True)(context) for c in self.conditions)

    def to_dict(self):
        return {
            "name": self.name,
            "description": getattr(self, "description", ""),
            "conditions": [getattr(c, "to_dict", lambda: {})() for c in self.conditions],
        }


class PolicyRegistry:
    def __init__(self, policies: List[Any]):
        self._policies = {p.name: p for p in policies}

    def list_all(self) -> List[Any]:
        return list(self._policies.values())

    def get(self, name: str) -> Any:
        return self._policies.get(name)


def get_policy_registry():
    # Return a registry object with list/get semantics expected by the API
    default = ChannelPolicy("default")
    cond = ConditionalPolicy("conditional-example")
    return PolicyRegistry([POLICY_READ_ONLY, default, cond])
