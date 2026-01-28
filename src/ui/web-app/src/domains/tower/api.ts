import type { ObservabilityStats, PatternAlert } from '@web-src/domains/tower/types';
import { fetchJson } from '@web-src/shared/client';

export const fetchPatternAlerts = (limit = 6) =>
    fetchJson<{ alerts: PatternAlert[] }>(`/api/ops/patterns/alerts?limit=${limit}`);

export const fetchObservabilityStats = () => fetchJson<ObservabilityStats>('/api/system/observability/stats');

export const runPatternDetection = (limit = 10) =>
    fetchJson<{
        analyzed_events: number;
        alerts_found: number;
        alerts: PatternAlert[];
        fallback: boolean
    }>(`/api/ops/patterns/alerts?limit=${limit}`);

// Policies
export const listPolicies = () => fetchJson<{ policies: any[] }>('/policies');
export const getPolicy = (name: string) => fetchJson<any>(`/policies/${name}`);

// Trace Visualization
export const fetchTraceGraph = (traceId: string) => fetchJson<any>(`/observability/trace/${traceId}/graph`);
export const fetchTraces = (limit = 50) => fetchJson<any>(`/observability/traces?limit=${limit}`);

// Events
export const fetchEvents = () => fetchJson<any>('/api/events');
