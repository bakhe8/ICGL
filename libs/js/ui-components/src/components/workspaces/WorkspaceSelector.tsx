import React, { useState } from "react";

export type Workspace = {
  id: string;
  name: string;
  mode?: string;
  created_at?: string;
};

export interface WorkspaceSelectorProps {
  workspaces: Workspace[];
  currentWorkspace?: string;
  onSwitch?: (id: string) => void;
  onCreate?: (name: string) => void | Promise<void>;
}

const modeBadgeColor = (mode?: string) => {
  switch (mode) {
    case "NORMAL":
      return "bg-blue-500";
    case "SANDBOX":
      return "bg-yellow-500";
    case "JOURNAL":
      return "bg-purple-500";
    default:
      return "bg-gray-500";
  }
};

export const WorkspaceSelector: React.FC<WorkspaceSelectorProps> = ({
  workspaces,
  currentWorkspace,
  onSwitch,
  onCreate,
}) => {
  const [newWorkspaceName, setNewWorkspaceName] = useState<string>("");

  const handleWorkspaceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedWorkspaceId = event.target.value;
    onSwitch?.(selectedWorkspaceId);
  };

  const handleCreateWorkspace = async () => {
    if (!newWorkspaceName.trim()) return;
    await onCreate?.(newWorkspaceName.trim());
    setNewWorkspaceName("");
  };

  const currentMode = workspaces.find((ws) => ws.id === currentWorkspace)?.mode;

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
          <span className={`inline-block h-2 w-2 rounded-full ${modeBadgeColor(currentMode)}`}></span>
          <span className="ml-2 text-sm text-gray-500">{currentMode || "Unknown"}</span>
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
