import unittest

class TestAgentVisibility(unittest.TestCase):
    def setUp(self):
        # Setup code to initialize the environment and agents
        self.agents = [
            {"id": 1, "name": "Agent A", "visible": True},
            {"id": 2, "name": "Agent B", "visible": False},
            {"id": 3, "name": "Agent C", "visible": True}
        ]

    def test_agent_visibility(self):
        # Test to ensure that only visible agents are returned
        visible_agents = [agent for agent in self.agents if agent["visible"]]
        
        # Expected result
        expected_visible_agents = [
            {"id": 1, "name": "Agent A", "visible": True},
            {"id": 3, "name": "Agent C", "visible": True}
        ]
        
        self.assertEqual(visible_agents, expected_visible_agents, "Visible agents do not match expected output")

if __name__ == '__main__':
    unittest.main()