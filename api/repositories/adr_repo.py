from pathlib import Path
from typing import List, Optional
from api.repositories.base_repo import BaseFileRepository
from api.dependencies import root_dir

# For now, we point to the existing file, or a new clean one.
# server.py used to use an in-memory KB which loaded from files.
# We will use a dedicated JSON for persistence in this Phase.
ADR_FILE = root_dir / "data" / "kb_adrs.json"

class AdrRepository(BaseFileRepository):
    def __init__(self):
        super().__init__(ADR_FILE)

    def get_latest(self) -> Optional[dict]:
        data = self.get_all()
        if not data:
            return None
        # Assuming data has created_at or we sort by index
        return data[-1] 
    
    def find_by_id(self, adr_id: str) -> Optional[dict]:
        data = self.get_all()
        for item in data:
            if item.get("id") == adr_id:
                return item
        return None
