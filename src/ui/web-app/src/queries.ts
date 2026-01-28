import { fetchJson, postJson } from './client';
import type {
  AITerminalResponse,
  AgentRegistryEntry,
  AgentRunResult,
  ChatResponse,
  Conflict,
  Decision,
  DocNode,
  GovernanceEvent,
  HRRecord,
  ObservabilityStats,
  PatternAlert,
  Proposal,
  ProposalState,
  SystemHealth,
  SystemStatus,
} from './types';

// Placeholder types to avoid 'any'
// type DashboardStats = Record<string, unknown>; // Unused
type QuickStats = Record<string, unknown>;

// --- System (real endpoints available in api/server.py) ---
export const fetchSystemHealth = () => fetchJson<SystemHealth>('/api/system/health');
export const fetchSystemStatus = () => fetchJson<SystemStatus>('/api/system/status');
// Note: fallback to observability stats until dedicated dashboard endpoint exists
export const fetchDashboardQuick = () => fetchJson<QuickStats>('/api/system/observability/stats');

// --- Chat ---
// Real governed chat entrypoint; no mock fallback.
// Previously /chat/free -> now routed to /chat (governed path)
export const sendFreeChatMessage = (payload: { message: string; session_id?: string; paths?: string[]; extra_context?: string; auto_execute?: boolean; actor?: string }) =>
  postJson<ChatResponse>('/chat', payload);

export const sendChatMessage = (payload: { message: string; session_id?: string; actor?: string; auto_execute?: boolean }) =>
  postJson<ChatResponse>('/chat', payload);

export const runAITerminal = (payload: { cmd: string; path?: string; lines?: number; content?: string }) =>
  postJson<AITerminalResponse>('/api/chat/terminal', payload);

export const writeAIFile = (payload: { path: string; content: string; mode?: 'w' | 'a' }) =>
  postJson<{ status: string; file?: string; path?: string; message?: string }>('/api/chat/file/write', payload);


// --- Governance ---
export const createProposal = (payload: {
  title: string;
  context: string;
  decision: string;
  reason?: string;
  impact?: string;
  human_id?: string;
}) =>
  postJson<{ status: string; adr_id?: string }>('/api/governance/proposals/create', {
    title: payload.title,
    context: [payload.context, payload.reason, payload.impact].filter(Boolean).join('\n'),
    decision: payload.decision,
    human_id: payload.human_id || 'bakheet',
  });

export const listProposals = (state?: ProposalState) =>
  fetchJson<{ proposals: Proposal[] }>(state ? `/api/governance/proposals?state=${state}` : '/api/governance/proposals');

export const updateProposal = (proposalId: string, payload: Partial<{ state: ProposalState; comment: string; tags: string[]; assigned_agents: string[] }>) =>
  fetchJson<{ proposal: Proposal }>(`/api/governance/proposals/${proposalId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

export const listDecisions = () => fetchJson<{ decisions: Decision[] }>('/api/governance/decisions');
export const getLatestAdr = () => fetchJson<Record<string, unknown>>('/api/governance/adr/latest');


// --- Observability ---
export const fetchPatternAlerts = (limit = 6) =>
  fetchJson<{ alerts: PatternAlert[] }>(`/api/ops/patterns/alerts?limit=${limit}`);

export const fetchObservabilityStats = () => fetchJson<ObservabilityStats>('/api/system/observability/stats');


// --- HR ---
export const fetchHRRecords = () => fetchJson<{ records: HRRecord[] }>('/api/hr/records');
export const addHRRecord = (record: HRRecord) => postJson<{ records: HRRecord[] }>('/api/hr/records/add', record);

// --- Agents ---
export const fetchAgentsRegistry = () => fetchJson<{ agents: AgentRegistryEntry[] }>('/api/system/agents');

// Fixed return type to match AgentRunResult interface
// Real implementation linked to backend
export const runAgent = (agentId: string, payload: { title: string; context: string }) =>
  postJson<{ status: string; agent: string; result?: AgentRunResult }>(`/api/system/agents/${agentId}/run`, payload);

export const listConflicts = () => fetchJson<{ conflicts: Conflict[] }>('/api/governance/conflicts');

// --- Observability (Mock) ---
export const runPatternDetection = (limit = 10) =>
  fetchJson<{
    analyzed_events: number;
    alerts_found: number;
    alerts: PatternAlert[];
    fallback: boolean
  }>(`/api/ops/patterns/alerts?limit=${limit}`);

// --- Governance Extensions ---
export const listGovernanceTimeline = () => fetchJson<{ timeline: GovernanceEvent[] }>('/api/governance/timeline');
export const listTimeline = () => listGovernanceTimeline();
export const createConflict = (payload: Partial<Conflict>) =>
  postJson<{ status: string; conflict: Conflict }>('/api/governance/conflicts', payload);
export const createDecision = (payload: { proposal_id: string; action: 'APPROVE' | 'REJECT'; rationale: string; human_id?: string }) =>
  postJson<{ status: string; result?: any }>(
    `/api/governance/sign/${payload.proposal_id}`,
    { ...payload, human_id: payload.human_id || 'bakheet' },
  );

// --- Docs ---
export const fetchDocsTree = () => fetchJson<{ roots: DocNode[] }>('/api/system/docs/tree');

export const fetchDocContent = (path: string) =>
  fetchJson<{ path: string; content: string; mime: string }>(`/api/system/docs/content?path=${encodeURIComponent(path)}`);
export const listAIWorkspace = (path = '.', limit = 200) =>
  fetchJson<{ files: { path: string; type: string; size?: number; modified?: string }[]; status: string }>(
    `/api/workspace?path=${encodeURIComponent(path)}&limit=${limit}`,
  );
export const readAIFile = (path: string) =>
  fetchJson<{ path: string; content: string; size?: number }>(`/api/workspace/read?path=${encodeURIComponent(path)}`);
export const saveDocContent = (payload: { path: string; content: string }) =>
  postJson<{ status: string; path: string }>('/api/system/docs/save', payload);

// --- Agents registry & gaps ---
export const fetchAgentsList = () => fetchJson<{ total: number; agents: AgentRegistryEntry[] }>('/api/agents/list');
export const fetchAgentGaps = () =>
  fetchJson<{ total_gaps: number; critical: { name: string; priority: string }[]; medium: { name: string; priority: string }[]; enhancement: { name: string; priority: string }[] }>(
    '/api/agents/gaps',
  );
