from pathlib import Path
from typing import Any
from api.repositories.base_repo import BaseFileRepository
from api.dependencies import root_dir

METADATA_FILE = root_dir / "data" / "kb_metadata.json"

class MetadataRepository(BaseFileRepository):
    def __init__(self):
        super().__init__(METADATA_FILE)

    def get_value(self, key: str, default: Any = None) -> Any:
        # We store as list of dicts: [{"key": "k", "value": "v"}, ...]
        for item in self.get_all():
            if item.get("key") == key:
                return item.get("value")
        return default

    def set_value(self, key: str, value: Any):
        data = self.get_all()
        found = False
        for i, item in enumerate(data):
            if item.get("key") == key:
                data[i]["value"] = value
                found = True
                break
        if not found:
            data.append({"key": key, "value": value})
        self._save_data(data)
