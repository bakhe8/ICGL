
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
}
