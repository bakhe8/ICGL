"""
Repo Map Builder
----------------

Lightweight repository map for Cycle 8 acceptance.
Generates a simple graph with nodes (dirs/files) and edges (parent -> child),
plus summary statistics.
"""

import os
from pathlib import Path
from typing import Dict, Any, List


def build_repo_map(root: str | os.PathLike = ".", max_files: int = 5000) -> Dict[str, Any]:
    """
    Build a simple repo map for the given root.

    Returns:
        {
          "nodes": [{"id": "...", "type": "dir|file", "path": "..."}],
          "edges": [{"from": "...", "to": "..."}],
          "stats": {"total_files": int, "total_dirs": int}
        }
    """
    root_path = Path(root).resolve()
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    total_files = 0
    total_dirs = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        if total_files >= max_files:
            break

        # Directory node
        rel_dir = Path(dirpath).relative_to(root_path)
        dir_id = str(rel_dir) if str(rel_dir) != "." else "."
        nodes.append({"id": dir_id, "type": "dir", "path": str(rel_dir)})
        total_dirs += 1

        # Child directories
        for d in dirnames:
            child_path = rel_dir / d if str(rel_dir) != "." else Path(d)
            edges.append({"from": dir_id, "to": str(child_path)})

        # Files
        for f in filenames:
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

