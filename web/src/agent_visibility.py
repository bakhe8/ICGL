from typing import List

class Agent:
    def __init__(self, name: str, position: tuple, visible: bool = False):
        self.name = name
        self.position = position
        self.visible = visible

    def update_visibility(self, obstacles: List[tuple], visibility_range: float) -> None:
        """
        Update the visibility status of the agent based on its position and obstacles.

        :param obstacles: List of positions representing obstacles.
        :param visibility_range: The range within which the agent can be visible.
        """
        self.visible = self._is_visible(obstacles, visibility_range)

    def _is_visible(self, obstacles: List[tuple], visibility_range: float) -> bool:
        """
        Determine if the agent is visible based on its position and obstacles.

        :param obstacles: List of positions representing obstacles.
        :param visibility_range: The range within which the agent can be visible.
        :return: True if the agent is visible, False otherwise.
        """
        # Example logic: Check if the agent is within visibility range and not blocked by obstacles
        for obstacle in obstacles:
            if self._distance_to(obstacle) < visibility_range:
                return False
        return True

    def _distance_to(self, other_position: tuple) -> float:
        """
        Calculate the Euclidean distance from the agent to another position.

        :param other_position: The position to calculate the distance to.
        :return: The Euclidean distance.
        """
        return ((self.position[0] - other_position[0]) ** 2 + (self.position[1] - other_position[1]) ** 2) ** 0.5

# Example usage
if __name__ == "__main__":
    agent = Agent(name="Agent1", position=(5, 5))
    obstacles = [(3, 3), (7, 8)]
    visibility_range = 10.0

    agent.update_visibility(obstacles, visibility_range)
    print(f"Agent {agent.name} visibility: {agent.visible}")