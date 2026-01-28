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
  required_agents?: string[];
  summoning_rationale?: string;
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

export interface HRRecord {
  name: string;
  role: string;
  duties: string[];
  limits: string[];
}

export interface ChatMessage {
  role: 'user' | 'system' | 'assistant';
  content: string;
  text?: string;
  blocks?: unknown[];
  timestamp?: string;
}

export interface ToolCall {
  cmd: string;
  path?: string;
  content?: string;
  status?: string;
  output?: string;
  proposed?: ToolCall;
}

export interface ChatResponse {
  messages: ChatMessage[];
  state: Record<string, unknown>;
  suggestions: string[];
  executed?: ToolCall[];
  blocked_commands?: ToolCall[];
  commands?: ToolCall[];
  text?: string;
  intent?: string;
}

export interface AIFileEntry {
  path: string;
  size: number;
}

export interface AITerminalResponse {
  output: string;
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
export interface ObservabilityStats {
  total_events: number;
  latest_event?: {
    message: string;
    timestamp: string;
  };
  average_purpose_score?: number;
  cycle_token_usage?: number;
  budget_limit?: number;
}

export interface Telemetry {
  drift_detection_count: number;
  agent_failure_count: number;
  last_latency_ms: number;
}

export interface SystemStatus {
  mode: string;
  waiting_for_human: boolean;
  active_alert_level: 'NONE' | 'HIGH' | 'CRITICAL';
  last_adr_id: string | null;
  telemetry: Telemetry;
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
