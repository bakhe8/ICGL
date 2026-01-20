from pathlib import Path
from api.repositories.base_repo import BaseFileRepository
from api.dependencies import root_dir

DECISIONS_FILE = root_dir / "data" / "kb_decisions.json"


class DecisionRepository(BaseFileRepository):
    def __init__(self):
        super().__init__(DECISIONS_FILE)
