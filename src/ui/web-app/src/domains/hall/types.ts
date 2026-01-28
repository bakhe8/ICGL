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

export interface HRRecord {
    name: string;
    role: string;
    duties: string[];
    limits: string[];
}
