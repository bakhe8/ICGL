from typing import List

class Environment:
    def __init__(self, obstacles: List[tuple]):
        self.obstacles = obstacles

    def is_visible(self, position: tuple) -> bool:
        # Simplified visibility check logic
        return position not in self.obstacles

class Agent:
    def __init__(self, position: tuple):
        self.position = position

    def check_visibility(self, environment: Environment) -> bool:
        """
        Perform a final check to determine if the agent is visible in the given environment.

        :param environment: The environment in which to check visibility.
        :return: True if the agent is visible, False otherwise.
        """
        return environment.is_visible(self.position)

# Example usage
if __name__ == "__main__":
    env = Environment(obstacles=[(1, 2), (3, 4)])
    agent = Agent(position=(2, 2))
    is_visible = agent.check_visibility(env)
    print(f"Agent visibility: {is_visible}")