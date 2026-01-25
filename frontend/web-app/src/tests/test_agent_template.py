import unittest
from backend.agents.template import BaseAgentTemplate, get_registered_agents
from backend.agents.performance_agent import PerformanceAgent

class TestAgentTemplate(unittest.TestCase):
    def test_agent_registration(self):
        agents = get_registered_agents()
        self.assertIn('PerformanceAgent', agents)
        self.assertIs(agents['PerformanceAgent'], PerformanceAgent)

    def test_performance_agent(self):
        agent = PerformanceAgent(role="tester", config={"key": "value"})
        self.assertEqual(agent.role, "tester")
        self.assertEqual(agent.config, {"key": "value"})
        self.assertIsNone(agent.analyze())  # Assuming analyze prints output

if __name__ == '__main__':
    unittest.main()