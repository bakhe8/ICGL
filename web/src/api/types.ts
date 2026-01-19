export type AgentStatus = 'active' | 'mock';
export type AgentFidelity = 'live' | 'simulated' | 'roadmap';

export interface AgentRegistryEntry {
  id: string;
  name: string;
  department: string;
  status: AgentStatus;
  fidelity: AgentFidelity;
  description: string;
  capabilities: string[];
  signals?: string[];
  role?: string;
  cycle?: string;
  registryRegistered?: boolean;
}

export interface AgentsRegistryResponse {
  agents: AgentRegistryEntry[];
  last_updated?: string;
}

export interface DocNode {
  name: string;
  path: string;
  type: 'directory' | 'file';
  size?: number;
  modified?: string;
  children?: DocNode[];
}

export interface DocsTreeResponse {
  roots: DocNode[];
}

export interface DocContentResponse {
  path: string;
  mime: string;
  content: string;
}

export interface PatternAlert {
  alert_id: string;
  severity: string;
  pattern: string;
  description: string;
  timestamp: string;
  event_count: number;
}

export interface SystemHealth {
  integrity_score: number;
  status: string;
  active_agents: number;
  active_operations: number;
  waiting_for_human?: boolean;
}

export interface AgentRunResult {
  agent: string;
  role: string;
  confidence: number;
  analysis: string;
  recommendations: string[];
  concerns: string[];
  references?: string[];
}

export interface PatternDetectionResult {
  analyzed_events: number;
  alerts_found: number;
  alerts: {
    alert_id: string;
    severity: string;
    pattern: string;
    description: string;
  }[];
  fallback?: boolean;
}

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
}

export interface Decision {
  id: string;
  proposal_id: string;
  decision: DecisionState;
  rationale: string;
  signed_by: string;
  created_at: string;
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
  payload: Record<string, any>;
}
