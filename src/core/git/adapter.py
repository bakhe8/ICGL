"""Minimal GitAdapter shim for dev environments.

This adapter implements the small surface the codebase expects:
- `stage_file(path)`
- `commit(message)`

It performs no real git operations and returns placeholders; replace
with a real adapter when enabling automated commits.
"""


class GitAdapter:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def stage_file(self, path: str) -> bool:
        # No-op staging in shim.
        return True

    def commit(self, message: str) -> str:
        # Return a fake commit hash placeholder.
        return "0000000-shim-commit"
