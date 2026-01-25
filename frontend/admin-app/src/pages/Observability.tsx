import { useState, useEffect } from 'react';
import { TraceVisualization } from '@admin-ui/components/TraceVisualization';
import './Observability.css';

interface TraceSummary {
    trace_id: string;
    start_time: string;
    end_time: string;
    event_count: number;
    adr_id: string | null;
    session_id: string | null;
}

export default function Observability() {
    const [traces, setTraces] = useState<TraceSummary[]>([]);
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTraces();
    }, []);

    const fetchTraces = async () => {
        try {
            setLoading(true);
            const res = await fetch('http://127.0.0.1:8000/observability/traces?limit=50');
            const data = await res.json();
            setTraces(data.traces || []);
        } catch (err) {
            console.error('Failed to fetch traces:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="observability-page">
            <div className="traces-list-sidebar">
                <div className="sidebar-header">
                    <h2>🔍 Traces</h2>
                    <button onClick={fetchTraces}>↻</button>
                </div>
                <div className="traces-list">
                    {loading ? (
                        <div className="loading">Loading...</div>
                    ) : (
                        traces.map(trace => (
                            <div
                                key={trace.trace_id}
                                className={`trace-item ${selectedTraceId === trace.trace_id ? 'selected' : ''}`}
                                onClick={() => setSelectedTraceId(trace.trace_id)}
                            >
                                <div className="trace-meta">
                                    <span className="trace-time">
                                        {new Date(trace.start_time).toLocaleTimeString()}
                                    </span>
                                    <span className="trace-count badge">
                                        {trace.event_count} evts
                                    </span>
                                </div>
                                <div className="trace-id">{trace.trace_id.slice(0, 8)}...</div>
                                {trace.adr_id && (
                                    <div className="trace-adr">ADR: {trace.adr_id}</div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>
            <div className="trace-view-main">
                {selectedTraceId ? (
                    <TraceVisualization traceId={selectedTraceId} />
                ) : (
                    <div className="empty-state">
                        <h3>Select a trace to visualize</h3>
                        <p>View agent thought processes and system events.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
