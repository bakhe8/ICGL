from shared.python.agents.template import BaseAgentTemplate, register_agent

class PerformanceAgent(BaseAgentTemplate):
    def analyze(self) -> None:
        print(f"Analyzing performance with role: {self.role} and config: {self.config}")

# Register the PerformanceAgent
register_agent(PerformanceAgent)