from dataclasses import dataclass
from typing import Dict, Type, Any

# Simple agent template registry
_registry: Dict[str, Type] = {}

def register_agent(name: str):
    def decorator(cls):
        _registry[name] = cls
        return cls
    return decorator

@dataclass
class BaseAgentTemplate:
    role: str
    config: Dict[str, Any]

    def analyze(self):
        # placeholder behavior
        return None

@register_agent('PerformanceAgent')
class PerformanceAgent(BaseAgentTemplate):
    pass


def get_registered_agents() -> Dict[str, Type]:
    return _registry
