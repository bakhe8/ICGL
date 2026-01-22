from enum import Enum

class WorkspaceMode(Enum):
    NORMAL = "normal"  # for regular work
    SANDBOX = "sandbox"  # for experimentation (isolated, temporary)
    JOURNAL = "journal"  # for private thoughts (no auto-analysis)

# Existing exports
__all__ = [
    # other exports
    "WorkspaceMode",
]