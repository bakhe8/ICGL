import { useEffect, useState } from 'react';
import './TraceVisualization.css';

/**
 * Advanced Trace Visualization
 * 
 * Interactive timeline showing complete event flow with expandable details.
 */

interface TraceNode {
    id: string;
    index: number;
    type: string;
    actor: string;
    actor_type: string;
    timestamp: string;
    status: string;
    data: {
        action?: string;
        target?: string;
        duration_ms?: number;
        error?: string;
        input_size?: number;
        output_size?: number;
        description_ar?: string;
    };
    tags: Record<string, string>;
}

interface TraceEdge {
    from: string;
    to: string;
    label: string;
    duration_ms: number;
}

interface TraceMetadata {
    total_events: number;
    duration_ms: number;
    success_count: number;
    failure_count: number;
    success_rate: number;
    start_time: string;
    end_time: string;
    actors: string[];
    event_types: string[];
}

interface TraceGraph {
    trace_id: string;
    nodes: TraceNode[];
    edges: TraceEdge[];
    metadata: TraceMetadata;
}

interface Props {
    traceId: string;
}

export function TraceVisualization({ traceId }: Props) {
    const [graph, setGraph] = useState<TraceGraph | null>(null);
    const [selectedNode, setSelectedNode] = useState<TraceNode | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadTrace();
    }, [traceId]);

    const loadTrace = async () => {
        try {
            setLoading(true);
            setError(null);
            const res = await fetch(`http://127.0.0.1:8000/observability/trace/${traceId}/graph`);

            if (!res.ok) {
                throw new Error(`Failed to load trace: ${res.statusText}`);
            }

            const data = await res.json();
            setGraph(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load trace');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="trace-loading">
                <div className="spinner"></div>
                <p>Loading trace...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="trace-error">
                <h3>❌ Error</h3>
                <p>{error}</p>
                <button onClick={loadTrace}>Retry</button>
            </div>
        );
    }

    if (!graph) {
        return <div className="trace-empty">No trace data</div>;
    }

    return (
        <div className="trace-visualization">
            {/* Header with metadata */}
            <div className="trace-header">
                <h2>🔍 Trace: {graph.trace_id.slice(0, 8)}...</h2>
                <div className="trace-stats">
                    <div className="stat">
                        <strong>{graph.metadata.total_events}</strong>
                        <span>Events</span>
                    </div>
                    <div className="stat">
                        <strong>{graph.metadata.duration_ms.toFixed(0)}ms</strong>
                        <span>Duration</span>
                    </div>
                    <div className="stat">
                        <strong>{(graph.metadata.success_rate * 100).toFixed(0)}%</strong>
                        <span>Success Rate</span>
                    </div>
                    <div className="stat">
                        <strong>{graph.metadata.actors.length}</strong>
                        <span>Actors</span>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="trace-timeline">
                <div className="timeline-track">
                    {graph.nodes.map((node, idx) => (
                        <div key={node.id} className="timeline-item">
                            {/* Event Node */}
                            <div
                                className={`event-node event-${node.status} ${selectedNode?.id === node.id ? 'selected' : ''}`}
                                onClick={() => setSelectedNode(node)}
                            >
                                <div className="node-index">{idx + 1}</div>
                                <div className="node-icon">{getEventIcon(node.type)}</div>
                                <div className="node-info">
                                    <div className="node-type">{node.type}</div>
                                    <div className="node-actor">{node.actor}</div>
                                </div>
                                <div className="node-time">
                                    {new Date(node.timestamp).toLocaleTimeString()}
                                </div>
                            </div>

                            {/* Connector */}
                            {idx < graph.edges.length && (
                                <div className="timeline-connector">
                                    <div className="connector-line"></div>
                                    <div className="connector-label">
                                        {graph.edges[idx].label}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Details Panel */}
            {selectedNode && (
                <div className="trace-details">
                    <div className="details-header">
                        <h3>Event Details</h3>
                        <button onClick={() => setSelectedNode(null)}>✕</button>
                    </div>

                    <div className="details-content">
                        {selectedNode.data.description_ar && (
                            <div className="detail-section secretary-enrichment">
                                <h4>💼 Sovereign Secretary Insight</h4>
                                <div className="arabic-insight" dir="rtl">
                                    {selectedNode.data.description_ar}
                                </div>
                            </div>
                        )}
                        <div className="detail-section">
                            <h4>General</h4>
                            <div className="detail-row">
                                <span>ID:</span>
                                <code>{selectedNode.id}</code>
                            </div>
                            <div className="detail-row">
                                <span>Type:</span>
                                <strong>{selectedNode.type}</strong>
                            </div>
                            <div className="detail-row">
                                <span>Actor:</span>
                                <strong>{selectedNode.actor}</strong>
                            </div>
                            <div className="detail-row">
                                <span>Actor Type:</span>
                                <span>{selectedNode.actor_type}</span>
                            </div>
                            <div className="detail-row">
                                <span>Status:</span>
                                <span className={`status-badge status-${selectedNode.status}`}>
                                    {selectedNode.status}
                                </span>
                            </div>
                        </div>

                        {selectedNode.data.action && (
                            <div className="detail-section">
                                <h4>Action</h4>
                                <div className="detail-row">
                                    <span>Action:</span>
                                    <strong>{selectedNode.data.action}</strong>
                                </div>
                                {selectedNode.data.target && (
                                    <div className="detail-row">
                                        <span>Target:</span>
                                        <strong>{selectedNode.data.target}</strong>
                                    </div>
                                )}
                                {selectedNode.data.duration_ms !== undefined && (
                                    <div className="detail-row">
                                        <span>Duration:</span>
                                        <strong>{selectedNode.data.duration_ms}ms</strong>
                                    </div>
                                )}
                            </div>
                        )}

                        {selectedNode.data.error && (
                            <div className="detail-section error-section">
                                <h4>❌ Error</h4>
                                <div className="error-message">{selectedNode.data.error}</div>
                            </div>
                        )}

                        {Object.keys(selectedNode.tags).length > 0 && (
                            <div className="detail-section">
                                <h4>Tags</h4>
                                {Object.entries(selectedNode.tags).map(([key, value]) => (
                                    <div key={key} className="detail-row">
                                        <span>{key}:</span>
                                        <code>{value}</code>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="detail-section">
                            <h4>Data Size</h4>
                            <div className="detail-row">
                                <span>Input:</span>
                                <span>{selectedNode.data.input_size || 0} bytes</span>
                            </div>
                            <div className="detail-row">
                                <span>Output:</span>
                                <span>{selectedNode.data.output_size || 0} bytes</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function getEventIcon(eventType: string): string {
    const icons: Record<string, string> = {
        'user_message': '💬',
        'llm_called': '🤖',
        'agent_analysis': '🔍',
        'kb_query': '📚',
        'kb_mutation': '✏️',
        'policy_check': '🔐',
        'channel_created': '🔀',
        'channel_message': '📨',
        'channel_closed': '🔴',
        'sentinel_alert': '⚠️',
        'gbe_validation': '✅'
    };
    return icons[eventType] || '📍';
}

export default TraceVisualization;
