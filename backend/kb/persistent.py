from typing import Dict, Optional, List
from .workspace import Workspace

class Persistent:
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}

    def add_workspace(self, workspace: Workspace) -> None:
        '''Store or update a workspace'''
        self.workspaces[workspace.id] = workspace

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        '''Retrieve workspace by ID'''
        return self.workspaces.get(workspace_id)

    def list_workspaces(self) -> List[Workspace]:
        '''List all workspaces'''
        return list(self.workspaces.values())

    def remove_workspace(self, workspace_id: str) -> bool:
        '''Remove a workspace, returns True if existed'''
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            return True
        return False