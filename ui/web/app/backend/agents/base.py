from enum import Enum

class AgentRole(Enum):
    BUILDER = "builder"
    VERIFICATION = "verification"  # Added new role

class Agent:
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role

class Problem:
    # Assuming Problem class is defined here
    pass

class AgentResult:
    def __init__(self, analysis: str, concerns: list, recommendations: list, confidence: float):
        self.analysis = analysis
        self.concerns = concerns
        self.recommendations = recommendations
        self.confidence = confidence