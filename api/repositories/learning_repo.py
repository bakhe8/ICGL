from pathlib import Path
from api.repositories.base_repo import BaseFileRepository
from api.dependencies import root_dir

LEARNING_FILE = root_dir / "data" / "kb_learning_log.json"

class LearningRepository(BaseFileRepository):
    def __init__(self):
        super().__init__(LEARNING_FILE)

    def add_log(self, log: dict):
        # Auto-increment cycle if not provided
        if "cycle" not in log:
            current = self.get_all()
            log["cycle"] = len(current) + 1
        return self.add(log)
