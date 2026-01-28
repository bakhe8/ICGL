import type { ADR, Conflict, Decision, GovernanceEvent, Proposal, ProposalState } from '@web-src/domains/desk/types';
import { fetchJson, postJson } from '@web-src/shared/client';

// Governance
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
export const listConflicts = () => fetchJson<{ conflicts: Conflict[] }>('/api/governance/conflicts');

export const createConflict = (payload: Partial<Conflict>) =>
    postJson<{ status: string; conflict: Conflict }>('/api/governance/conflicts', payload);

export const createDecision = (payload: { proposal_id: string; action: 'APPROVE' | 'REJECT'; rationale: string; human_id?: string }) =>
    postJson<{ status: string; result?: any }>(
        `/api/governance/sign/${payload.proposal_id}`,
        { ...payload, human_id: payload.human_id || 'bakheet' },
    );

export const listGovernanceTimeline = () => fetchJson<{ timeline: GovernanceEvent[] }>('/api/governance/timeline');
export const listTimeline = () => listGovernanceTimeline();

// ADRs
export const listAdrs = () => fetchJson<{ adrs: ADR[] }>('/kb/adrs');
export const deleteAdr = (adrId: string) => fetchJson<{ status: string }>(`/kb/adr/${adrId}`, { method: 'DELETE' });

// Ideas / Analysis
export const fetchAnalysis = (id: string) => fetchJson<any>(`/api/analysis/${id}`);
export const fetchLatestAnalysis = () => fetchJson<any>('/api/analysis/latest');
export const fetchIdeaSummary = (id: string) => fetchJson<any>(`/api/idea-summary/${id}`);
export const runIdea = (payload: any) => postJson<any>('/api/idea-run', payload);
export const clarifyIdea = (payload: any) => postJson<any>('/api/governance/clarify', payload);
export const approveChanges = (payload: any) => postJson<any>('/api/governance/approve-changes', payload);
export const rebuildSystem = () => postJson<any>('/api/rebuild', {});
