import { fetchJson } from './client';
import type {
  AgentsRegistryResponse,
  DocsTreeResponse,
  PatternAlert,
  SystemHealth,
  AgentRunResult,
  DocContentResponse,
  PatternDetectionResult,
  Proposal,
  ProposalState,
  Conflict,
  Decision,
  GovernanceEvent,
} from './types';
import { postJson } from './client';

export const fetchAgentsRegistry = () => fetchJson<AgentsRegistryResponse>('/api/agents/registry');
export const fetchDocsTree = () => fetchJson<DocsTreeResponse>('/api/docs/tree');
export const fetchDocContent = (path: string) =>
  fetchJson<DocContentResponse>(`/api/docs/content?path=${encodeURIComponent(path)}`);
export const fetchSystemHealth = () => fetchJson<SystemHealth>('/system/health');
export const fetchPatternAlerts = (limit = 6) =>
  fetchJson<{ alerts: PatternAlert[] }>('/patterns/alerts?limit=' + limit);
export const runAgent = (agentRole: string, payload: { title: string; context: string }) =>
  postJson<AgentRunResult>(`/agents/${agentRole}/analyze`, payload);
export const runPatternDetection = (windowMinutes = 5) =>
  postJson<PatternDetectionResult>(`/patterns/detect`, { window_minutes: windowMinutes });

// Governance
export const createProposal = (payload: {
  title: string;
  description: string;
  reason: string;
  impact: string;
  risks: string;
  author?: string;
  alternatives?: string;
  cost_or_complexity?: string;
  execution_plan?: string;
  consultation_notes?: string;
  tags?: string[];
}) => postJson<{ proposal: Proposal }>('/api/governance/proposals', payload);

export const listProposals = (state?: ProposalState) =>
  fetchJson<{ proposals: Proposal[] }>(state ? `/api/governance/proposals?state=${state}` : '/api/governance/proposals');

export const updateProposal = (proposalId: string, payload: Partial<{ state: ProposalState; comment: string; tags: string[]; assigned_agents: string[] }>) =>
  fetchJson<{ proposal: Proposal }>(`/api/governance/proposals/${proposalId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

export const createDecision = (payload: { proposal_id: string; decision: string; rationale: string; signed_by?: string }) =>
  postJson<{ decision: Decision; proposal: Proposal }>('/api/governance/decisions', payload);

export const createConflict = (payload: { title: string; description: string; proposals?: string[]; involved_agents?: string[] }) =>
  postJson<{ conflict: Conflict }>('/api/governance/conflicts', payload);

export const updateConflict = (conflictId: string, payload: Partial<{ state: string; resolution: string; comment: string }>) =>
  fetchJson<{ conflict: Conflict }>(`/api/governance/conflicts/${conflictId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

export const listConflicts = (state?: string) =>
  fetchJson<{ conflicts: Conflict[] }>(state ? `/api/governance/conflicts?state=${state}` : '/api/governance/conflicts');

export const listDecisions = () => fetchJson<{ decisions: Decision[] }>('/api/governance/decisions');

export const listGovernanceTimeline = () => fetchJson<{ timeline: GovernanceEvent[] }>('/api/governance/timeline');
