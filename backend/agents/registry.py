import os
import importlib
from shared.python.agents.template import register_agent

def auto_register_agents(directory: str) -> None:
    """Automatically register agents by scanning the given directory."""
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"backend.agents.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, BaseAgentTemplate) and attribute is not BaseAgentTemplate:
                    register_agent(attribute)

# Automatically register agents in the 'agents' directory
auto_register_agents(os.path.dirname(__file__))