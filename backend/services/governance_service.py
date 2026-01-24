from typing import List, Optional

from backend.kb.schemas import ADR, HumanDecision

from .base import BaseService


class GovernanceService(BaseService):
    """
    Handles higher-level governance logic, separating it from the API layer.
    """

    async def get_all_adrs(self) -> List[ADR]:
        return list(self.storage.load_all_adrs().values())

    async def get_adr_by_id(self, adr_id: str) -> Optional[ADR]:
        return self.storage.load_adr(adr_id)

    async def create_adr(self, adr: ADR) -> None:
        self.storage.save_adr(adr)

    async def record_decision(self, decision: HumanDecision) -> None:
        self.storage.save_human_decision(decision)
