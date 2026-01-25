from dataclasses import dataclass, field
from typing import Dict
from .schemas import WorkspaceMode
from ..utils.time import now

@dataclass
class Workspace:
    """
    A Workspace represents an isolated environment within the system where different operations can be performed.
    
    Attributes:
        id (str): Unique identifier for the workspace.
        name (str): Human-readable name for the workspace.
        mode (WorkspaceMode): The operational mode of the workspace, which determines its isolation level.
            - NORMAL: Standard mode with typical isolation, suitable for regular operations.
            - SANDBOX: Highly isolated mode, used for testing and experimentation without affecting the main environment.
            - JOURNAL: A mode designed for logging and audit purposes, where changes are tracked meticulously.
        created_at (str): Timestamp of when the workspace was created. Defaults to the current time.
        metadata (Dict): Additional metadata associated with the workspace, stored as key-value pairs.
    """
    id: str
    name: str
    mode: WorkspaceMode
    created_at: str = field(default_factory=now)
    metadata: Dict = field(default_factory=dict)