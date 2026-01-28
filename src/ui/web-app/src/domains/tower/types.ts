export interface PatternAlert {
    alert_id: string;
    severity: string;
    pattern: string;
    description: string;
    timestamp: string;
    event_count: number;
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
