import math
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class VisibilityObstacle:
    """Represents an physical or logical obstacle in the agent environment."""

    id: str
    position: Tuple[float, float]
    radius: float = 1.0


@dataclass
class VisibilityState:
    """Visibility status of an agent."""

    is_visible: bool
    distance_to_nearest_obstacle: float
    blocked_by: List[str] = field(default_factory=list)


class VisibilityEngine:
    """
    Promoted engine for calculating agent visibility in a governed environment.
    Incorporates logic from legacy agent.py and agent_visibility.py.
    """

    def __init__(self, obstacles: List[VisibilityObstacle] = None):
        self.obstacles = obstacles or []

    def calculate_visibility_status(
        self, agent_pos: Tuple[float, float], visibility_range: float = 10.0
    ) -> VisibilityState:
        """
        Determines if an agent is visible and what blocks it.
        """
        blocked_by = []
        min_dist = float("inf")

        for obs in self.obstacles:
            dist = math.sqrt(
                (agent_pos[0] - obs.position[0]) ** 2
                + (agent_pos[1] - obs.position[1]) ** 2
            )

            # If agent is within the obstacle's radius, it's considered "hidden/blocked"
            if dist < obs.radius:
                blocked_by.append(obs.id)

            if dist < min_dist:
                min_dist = dist

        # Visibility logic: Not blocked and within range
        is_visible = len(blocked_by) == 0 and min_dist <= visibility_range

        return VisibilityState(
            is_visible=is_visible,
            distance_to_nearest_obstacle=min_dist if min_dist != float("inf") else 0.0,
            blocked_by=blocked_by,
        )


# Example singleton for the system
DEFAULT_ENGINE = VisibilityEngine(
    obstacles=[
        VisibilityObstacle("central_firewall", (5.0, 5.0), 2.0),
        VisibilityObstacle("data_silo_alpha", (12.0, 8.0), 1.5),
    ]
)
