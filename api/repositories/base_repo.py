import json
from pathlib import Path
from typing import List, Any, Optional

from api.dependencies import logger

class BaseFileRepository:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_data([]) # Initialize as empty list

    def _load_data(self) -> Any:
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: Any):
        self.file_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def get_all(self) -> List[Any]:
        return self._load_data()

    def add(self, item: Any) -> Any:
        data = self._load_data()
        data.append(item)
        self._save_data(data)
        return item
