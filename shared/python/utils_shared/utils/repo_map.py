import os
from pathlib import Path
from typing import Any, Dict, List

IGNORE_DIRS = {
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
    "data",
}
IGNORE_FILES = {".DS_Store", "package-lock.json", "yarn.lock", "poetry.lock"}


def build_repo_map(
    root: str | os.PathLike = ".", max_files: int = 5000, max_depth: int = 5
) -> Dict[str, Any]:
    """
    Build a simple repo map for the given root.
    """
    root_path = Path(root).resolve()
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    total_files = 0
    total_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        # 1. Check Max Files
        if total_files >= max_files:
            break

        rel_dir = Path(dirpath).relative_to(root_path)

        # 2. Check Depth
        depth = len(rel_dir.parts)
        if depth > max_depth:
            # Prevent deeper traversal
            dirnames[:] = []
            continue

        # 3. Filter Directories (in-place for os.walk)
        dirnames[:] = [
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        dir_id = str(rel_dir) if str(rel_dir) != "." else "."
        nodes.append({"id": dir_id, "type": "dir", "path": str(rel_dir)})
        total_dirs += 1

        # Process Children for edges
        for d in dirnames:
            child_path = rel_dir / d if str(rel_dir) != "." else Path(d)
            edges.append({"from": dir_id, "to": str(child_path)})

        # Process Files
        for f in filenames:
            if f in IGNORE_FILES or f.startswith("."):
                continue

            if total_files >= max_files:
                break

            file_path = rel_dir / f if str(rel_dir) != "." else Path(f)
            nodes.append({"id": str(file_path), "type": "file", "path": str(file_path)})
            edges.append({"from": dir_id, "to": str(file_path)})
            total_files += 1

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {"total_files": total_files, "total_dirs": total_dirs},
    }
