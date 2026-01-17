from typing import List

class ADR:
    def __init__(self, id: int, title: str, status: str):
        self.id = id
        self.title = title
        self.status = status

class ADRManager:
    def get_pending_adrs(self) -> List[ADR]:
        # Placeholder for retrieving pending ADRs
        # In a real implementation, this might query a database or read from a file
        return [ADR(1, "Use REST API for communication", "pending")]

    def review_adr(self, adr: ADR):
        # Placeholder for reviewing an ADR
        # This could involve updating the ADR status, adding comments, etc.
        print(f"Reviewing ADR: {adr.title}")