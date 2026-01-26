import React, { useEffect, useState } from 'react';
import { WorkspaceSelector as WorkspaceSelectorView, type Workspace } from '@icgl/ui-components';
import { fetchJson } from '../api/client';

interface WorkspaceProps {
  currentWorkspace?: string;
  onSwitch?: (id: string) => void;
}

const WorkspaceSelector: React.FC<WorkspaceProps> = ({ currentWorkspace, onSwitch }) => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);

  useEffect(() => {
    const fetchWorkspaces = async () => {
      try {
        const data = await fetchJson('/api/workspaces');
        if (Array.isArray(data)) {
          setWorkspaces(data as Workspace[]);
        } else {
          setWorkspaces([]);
        }
      } catch (error) {
        console.error('Error fetching workspaces:', error);
      }
    };

    fetchWorkspaces();
  }, []);

  const handleCreateWorkspace = async (name: string) => {
    try {
      const newWorkspace = await fetchJson('/api/workspaces', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name }),
      });
      if (newWorkspace && typeof newWorkspace === 'object' && 'id' in newWorkspace) {
        setWorkspaces([...workspaces, newWorkspace as Workspace]);
      }
    } catch (error) {
      console.error('Error creating workspace:', error);
    }
  };

  return (
    <WorkspaceSelectorView
      workspaces={workspaces}
      currentWorkspace={currentWorkspace}
      onSwitch={onSwitch}
      onCreate={handleCreateWorkspace}
    />
  );
};

export default WorkspaceSelector;
