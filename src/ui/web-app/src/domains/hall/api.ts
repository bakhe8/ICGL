import { fetchJson, postJson } from '../../shared/client';
import type { AgentRegistryEntry, AgentRunResult, HRRecord } from './types';

// Agents
export const fetchAgentGaps = () => fetchJson<{ total_gaps: number; critical: any[]; medium: any[]; enhancement: any[] }>('/api/agents/gaps');
export const runAgent = (agentId: string, payload: { title: string; context: string }) =>
    postJson<{ status: string; agent: string; result?: AgentRunResult }>(`/api/system/agents/${agentId}/run`, payload);

export const fetchAgentsList = () => fetchJson<{ total: number; agents: AgentRegistryEntry[] }>('/api/agents/list');
export const fetchAgents = fetchAgentsList; // Alias used in code

export const fetchAgentRole = (agentId: string) => fetchJson<any>(`/api/agents/${agentId}/role`);
export const fetchAgentHistory = (agentId: string) => fetchJson<any>(`/api/agents/${agentId}/history`);
export const fetchAgentStats = (agentId: string) => fetchJson<any>(`/api/agents/${agentId}/stats`);

// HR
export const fetchHRRecords = () => fetchJson<{ records: HRRecord[] }>('/api/hr/records');
export const addHRRecord = (record: HRRecord) => postJson<{ records: HRRecord[] }>('/api/hr/records/add', record);

// Mind Map
export const fetchMindGraph = () => fetchJson<any>('/api/mind/graph');

// Channels
export const fetchChannelStats = () => fetchJson<any>('/channels/stats');
export const fetchChannels = () => fetchJson<any>('/channels');
