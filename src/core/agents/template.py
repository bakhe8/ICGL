from typing import Dict, Type


class BaseAgentTemplate:
    role: str
    config: Dict

    def __init__(self, role: str, config: Dict):
        self.role = role
        self.config = config

    def analyze(self) -> None:
        raise NotImplementedError("Subclasses should implement this method.")


# Dictionary to hold registered agents
_registered_agents: Dict[str, Type[BaseAgentTemplate]] = {}


def register_agent(agent_class: Type[BaseAgentTemplate]) -> None:
    """Register an agent class for dynamic loading."""
    _registered_agents[agent_class.__name__] = agent_class


def get_registered_agents() -> Dict[str, Type[BaseAgentTemplate]]:
    """Return all registered agent classes."""
    return _registered_agents
