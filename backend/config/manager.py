import os
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigManager:
    """
    Robust configuration loader for ICGL.
    Prioritizes:
    1. Environment variables (ICGL_*)
    2. config.yaml in project root
    3. Sane defaults
    """

    def __init__(self, config_file: str = "config.yaml"):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.config_path = self.root_dir / config_file
        self.settings: Dict[str, Any] = self._load_defaults()
        self._load_from_yaml()
        self._load_from_env()

    def _load_defaults(self) -> Dict[str, Any]:
        return {
            "app_name": "ICGL",
            "version": "0.1.0",
            "auto_apply": False,
            "max_consensus_attempts": 3,
            "default_timeout": 30,
            "log_level": "INFO",
            "log_directory": "data/logs",
            "vector_store_path": "data/vector_store",
            "embedding_model": "text-embedding-3-small",
            "default_llm_model": "gpt-4-turbo-preview",
            "default_temperature": 0.0,
            "max_tokens": 1000,
        }

    def _load_from_yaml(self):
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    self.settings.update(data)
        except Exception as e:
            print(f"⚠️ Warning: Failed to load {self.config_path}: {e}")

    def _load_from_env(self):
        """Override with ICGL_* environment variables."""
        for key in self.settings.keys():
            env_key = f"ICGL_{key.upper()}"
            if env_key in os.environ:
                val = os.environ[env_key]
                # Basic type casting
                if isinstance(self.settings[key], bool):
                    self.settings[key] = val.lower() in ("true", "1", "yes")
                elif isinstance(self.settings[key], int):
                    self.settings[key] = int(val)
                elif isinstance(self.settings[key], float):
                    self.settings[key] = float(val)
                else:
                    self.settings[key] = val

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.settings[key]

    def __repr__(self) -> str:
        return f"ConfigManager({list(self.settings.keys())})"


# Singleton instance
config = ConfigManager()
