from backend.agents.template import BaseAgentTemplate, register_agent

@register_agent('PerformanceAgent')
class PerformanceAgent(BaseAgentTemplate):
    def analyze(self):
        return None
