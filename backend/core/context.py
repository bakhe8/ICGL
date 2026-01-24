import os
from pathlib import Path
from typing import List


class ContextBuilder:
    """
    The Cartographer: Maps the repository structure to provide context to Agents.
    """

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path).resolve()
        self.ignore_dirs = {
            ".git",
            "__pycache__",
            "venv",
            ".venv",
            "node_modules",
            ".pytest_cache",
            ".gemini",
            "dist",
            "build",
            ".idea",
            ".vscode",
        }
        self.ignore_files = {".DS_Store", "package-lock.json", "yarn.lock"}

    def generate_map(self, max_depth: int = 3) -> str:
        """
        Generates a tree-like string representation of the repo.
        """
        lines = ["PROJECT ROOT"]
        self._scan_dir(self.root, 0, max_depth, lines)
        return "\n".join(lines)

    def _scan_dir(
        self, current_path: Path, depth: int, max_depth: int, lines: List[str]
    ):
        if depth > max_depth:
            return

        try:
            # Sort: Dirs first, then files
            items = sorted(os.listdir(current_path))
            dirs = []
            files = []

            for item in items:
                if item in self.ignore_dirs or item in self.ignore_files:
                    continue
                # Ignore generic hidden files but allow critical ones if needed
                if item.startswith(".") and item not in [".env", ".gitignore"]:
                    continue

                full_path = current_path / item
                if full_path.is_dir():
                    dirs.append(item)
                else:
                    files.append(item)

            # Process Dirs
            for d in dirs:
                indent = "  " * (depth + 1)
                lines.append(f"{indent}📂 {d}/")
                self._scan_dir(current_path / d, depth + 1, max_depth, lines)

            # Process Files (only if not too deep to optimize token usage)
            if depth < max_depth:
                for f in files:
                    indent = "  " * (depth + 1)
                    lines.append(f"{indent}📄 {f}")

        except PermissionError:
            pass
