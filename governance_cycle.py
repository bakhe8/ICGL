import asyncio
from typing import List

from icgl.governance import ICGL
from icgl.kb.schemas import ADR, LearningLog, uid


class GovernanceCycle:
    def __init__(self, db_path: str = "data/kb.db"):
        self.icgl = ICGL(db_path=db_path)
        self._last_log_count = len(self.icgl.kb.learning_log)

    async def start_cycle(
        self,
        title: str,
        context: str,
        decision: str,
        human_id: str = "bakheet",
    ):
        """
        Initiates a real ICGL governance cycle and records learning logs.
        """
        adr = ADR(
            id=uid(),
            title=title,
            status="DRAFT",
            context=context,
            decision=decision,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        return await self.icgl.run_governance_cycle(adr, human_id=human_id)

    def get_logs(self) -> List[LearningLog]:
        """
        Returns all learning logs from the Knowledge Base.
        """
        return list(self.icgl.kb.learning_log)

    def get_new_logs(self) -> List[LearningLog]:
        """
        Returns only logs created since the last call.
        """
        logs = list(self.icgl.kb.learning_log[self._last_log_count:])
        self._last_log_count = len(self.icgl.kb.learning_log)
        return logs


# Example usage
if __name__ == "__main__":
    cycle = GovernanceCycle()
    asyncio.run(
        cycle.start_cycle(
            title="Governance cycle for learning logs",
            context="Trigger full governance cycle to generate learning logs.",
            decision="Run full cycle",
            human_id="bakheet",
        )
    )
    print("New Logs:", cycle.get_new_logs())