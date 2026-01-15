import yaml
import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._data: Dict[str, Any] = {}
        load_dotenv()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    @property
    def env(self) -> Dict[str, str]:
        return dict(os.environ)

config = Config()
