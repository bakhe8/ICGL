"""
Consensus AI — Token Budget Manager
===================================
Manages the "Hard Realism" economic constraints of the system.
Ensures no governance cycle exceeds its allocated resource cap.
"""

import os
from dataclasses import dataclass
from typing import Literal


@dataclass
class BudgetStatus:
    used: int
    limit: int
    state: Literal["NORMAL", "WARNING", "CRITICAL", "EXCEEDED"]
    percentage: float


class TokenBudget:
    """
    Authority on resource limits.
    "The System cannot think infinitely; it must think efficiently."
    """

    def __init__(self, default_limit: int = 50000):
        self._limit = int(os.getenv("ICGL_TOKEN_BUDGET", default_limit))

    def check_usage(self, current_usage: int) -> bool:
        """Returns True if usage is within limits, False if exceeded."""
        return current_usage < self._limit

    def get_status(self, current_usage: int) -> BudgetStatus:
        """Detailed status analysis."""
        pct = (current_usage / self._limit) * 100 if self._limit > 0 else 0

        state = "NORMAL"
        if pct >= 100:
            state = "EXCEEDED"
        elif pct >= 90:
            state = "CRITICAL"
        elif pct >= 70:
            state = "WARNING"

        return BudgetStatus(
            used=current_usage, limit=self._limit, state=state, percentage=pct
        )
