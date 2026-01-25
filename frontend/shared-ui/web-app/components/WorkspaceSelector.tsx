import React, { useEffect, useState } from 'react';
import { fetchJson } from '@web-src/api/client';

interface Workspace {
  id: string;
  name: string;
  mode: string;
  created_at: string;
}

interface WorkspaceProps {
  currentWorkspace?: string;
  onSwitch?: (id: string) => void;
}

const WorkspaceSelector: React.FC<WorkspaceProps> = ({ currentWorkspace, onSwitch }) => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [newWorkspaceName, setNewWorkspaceName] = useState<string>('');

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

  const handleCreateWorkspace = async () => {
    if (!newWorkspaceName) return;

    try {
      const newWorkspace = await fetchJson('/api/workspaces', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newWorkspaceName }),
      });
      if (newWorkspace && typeof newWorkspace === 'object' && 'id' in newWorkspace) {
        setWorkspaces([...workspaces, newWorkspace as Workspace]);
      }
      setNewWorkspaceName('');
    } catch (error) {
      console.error('Error creating workspace:', error);
    }
  };

  const handleWorkspaceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedWorkspaceId = event.target.value;
    if (onSwitch) {
      onSwitch(selectedWorkspaceId);
    }
  };

  const modeBadgeColor = (mode: string) => {
    switch (mode) {
      case 'NORMAL':
        return 'bg-blue-500';
      case 'SANDBOX':
        return 'bg-yellow-500';
      case 'JOURNAL':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="workspace-selector p-4 bg-white shadow-md rounded-md">
      <div className="mb-4">
        <label htmlFor="workspace-select" className="block text-sm font-medium text-gray-700">
          Select Workspace
        </label>
        <select
          id="workspace-select"
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          value={currentWorkspace}
          onChange={handleWorkspaceChange}
        >
          {workspaces.map((workspace) => (
            <option key={workspace.id} value={workspace.id}>
              {workspace.name}
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <span className={`inline-block h-2 w-2 rounded-full ${modeBadgeColor(currentWorkspace || '')}`}></span>
          <span className="ml-2 text-sm text-gray-500">
            {workspaces.find((ws) => ws.id === currentWorkspace)?.mode || 'Unknown'}
          </span>
        </div>
        <button
          type="button"
          className="ml-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          onClick={handleCreateWorkspace}
        >
          Create Workspace
        </button>
      </div>
      <input
        type="text"
        className="mt-2 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        placeholder="New workspace name"
        value={newWorkspaceName}
        onChange={(e) => setNewWorkspaceName(e.target.value)}
      />
    </div>
  );
};

export default WorkspaceSelector;
