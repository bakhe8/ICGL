import importlib
import os
from backend.agents import AgentRegistry, EngineerAgent, BuilderAgent
from capability_checker import CapabilityChecker

class ICGLSystem:
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.capability_checker = CapabilityChecker()

    def execute(self):
        if self.should_auto_apply():
            self.run_builder_agent()
            self.run_engineer_agent()
            self.reload_agents()

    def should_auto_apply(self) -> bool:
        # Load configuration to check if AUTO_APPLY is enabled
        import yaml
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config.get('auto_apply', False)

    def run_builder_agent(self):
        # Simulate the BuilderAgent generating code
        BuilderAgent().generate_code()

    def run_engineer_agent(self):
        # Automatically call EngineerAgent to write files
        EngineerAgent().write_files()

    def reload_agents(self):
        # Reload agent registry and re-import new agents
        self.agent_registry.reload()
        self.update_capability_checker()

    def update_capability_checker(self):
        # Update CapabilityChecker's agent list
        self.capability_checker.update_agents(self.agent_registry.get_agents())

    def auto_discover_new_agents(self):
        # Check backend/agents/ directory for new .py files
        new_agents = []
        for filename in os.listdir('backend/agents/'):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                new_agents.append(module_name)
        return new_agents

    def register_new_agents(self):
        new_agents = self.auto_discover_new_agents()
        for agent in new_agents:
            module = importlib.import_module(f'backend.agents.{agent}')
            self.agent_registry.register(module)

# Example usage
if __name__ == "__main__":
    icgl_system = ICGLSystem()
    icgl_system.execute()