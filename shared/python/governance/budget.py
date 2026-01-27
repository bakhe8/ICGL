"""
ICGL Governance — Budget Management
==================================

Stubs for budget tracking and economic guardianship.
"""

from dataclasses import dataclass
from typing import Any


class TokenBudget:
    def __init__(self):
        self.limit = 1000000
        self.used = 0

    def check_usage(self, current_tokens: int) -> bool:
        return current_tokens < self.limit

    def get_status(self, current_tokens: int) -> Any:
        @dataclass
        class Status:
            state: str
            used: int
            limit: int

        state = "HEALTHY"
        if current_tokens > self.limit * 0.8:
            state = "WARNING"
        return Status(state=state, used=current_tokens, limit=self.limit)


class BudgetManager:
    def __init__(self):
        self.total_tokens = 0
        self.budget_limit = 1000000

    def record_usage(self, agent_id: str, tokens: int):
        self.total_tokens += tokens


budget_manager = BudgetManager()
