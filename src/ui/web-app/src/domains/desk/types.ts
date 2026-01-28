export type ProposalState = 'open' | 'draft' | 'discussion' | 'ready' | 'decision' | 'archived';
export type DecisionState = 'pending' | 'approved' | 'rejected' | 'deferred';
export type ConflictState = 'open' | 'resolved' | 'archived';

export interface Proposal {
    id: string;
    title: string;
    description: string;
    author: string;
    reason: string;
    impact: string;
    risks: string;
    alternatives?: string;
    cost_or_complexity?: string;
    execution_plan?: string;
    consultation_notes?: string;
    state: ProposalState;
    tags: string[];
    created_at: string;
    updated_at: string;
    assigned_agents: string[];
    comments: string[];
    predicted_benefit?: string;
    actual_benefit?: string;
}

export interface Decision {
    id: string;
    proposal_id: string;
    decision: DecisionState;
    rationale: string;
    signed_by: string;
    created_at: string;
    timestamp: string;
}

export interface Conflict {
    id: string;
    title: string;
    description: string;
    proposals: string[];
    involved_agents: string[];
    state: ConflictState;
    created_at: string;
    updated_at: string;
    comments: string[];
    resolution?: string;
}

export interface GovernanceEvent {
    id: string;
    type: string;
    timestamp: string;
    label?: string;
    source?: string;
    severity?: string;
    payload: Record<string, unknown>;
}

export interface ADR {
    id: string;
    title: string;
    status: 'DRAFT' | 'ACCEPTED' | 'REJECTED';
    context: string;
    decision: string;
    created_at: string; // ISO string
    sentinel_signals?: string[];
    human_decision_id?: string | null;
}

// Importing AgentRunResult from Hall types if needed, but for now defining Synthesis types here
// Circular dependency might be an issue if specific types are needed.
// For SynthesisResult, it relies on AgentRunResult.
// I will separate it or use 'any' temporarily if needed, but better to import.
// However, in a pure types file, imports are fine.
// But to avoid circular imports between domains, maybe Shared is better for common types?
// AgentRunResult seems specific to Agents (Hall).
// I will rely on the barrel file or assume generic?
// Let's assume consuming code imports correctly.
// I'll put SynthesisResult here but I need AgentRunResult.
// I will import it from Hall types? No, that creates dependency Desk -> Hall.
// Maybe AgentRunResult belongs in Shared?
// "Agent Run" is a core system capability.
// Let's put AgentRunResult in Shared/Types or Hall/Types.
// Logic: Agents are Hall.
// Synthesis is Desk (Governance).
// Desk depends on Hall. That's acceptable (Strategy depends on Capabilities).

import type { AgentRunResult } from '../hall/types';

export interface SynthesisResult {
    overall_confidence: number;
    consensus_recommendations: string[];
    all_concerns: string[];
    agent_results: AgentRunResult[];
    semantic_matches: any[];
    sentinel_alerts: any[];
    mindmap: string;
    mediation?: {
        analysis: string;
        confidence: number;
        concerns: string[];
    };
    policy_report: any;
}

export interface SynthesisState {
    adr: ADR;
    status?: string;
    synthesis?: SynthesisResult;
    latency_ms?: number;
    error?: string;
}
