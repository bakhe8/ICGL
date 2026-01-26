from typing import Protocol, List
from dataclasses import dataclass

@dataclass
class GitStatus:
    is_clean: bool
    modified_files: List[str]
    staged_files: List[str]

class GitInterface(Protocol):
    """
    Abstract interface for Version Control operations.
    Enforces P-CORE-01 (Strategic Optionality).
    """
    
    def stage_file(self, path: str) -> None:
        """Stages a file for commit."""
        ...
        
    def commit(self, message: str) -> str:
        """Commits staged changes. Returns commit hash."""
        ...
        
    def get_status(self) -> GitStatus:
        """Returns current repo status."""
        ...
        
    def get_current_branch(self) -> str:
        """Returns active branch name."""
        ...
