import React, { useState } from "react";
import "./TraceVisualization.css";

export interface TraceNode {
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
  };
  tags: Record<string, string>;
}

export interface TraceEdge {
  from: string;
  to: string;
  label: string;
  duration_ms: number;
}

export interface TraceMetadata {
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

export interface TraceGraph {
  trace_id: string;
  nodes: TraceNode[];
  edges: TraceEdge[];
  metadata: TraceMetadata;
}

export interface TraceVisualizationProps {
  trace?: TraceGraph | null;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

const eventIcon = (eventType: string): string => {
  const icons: Record<string, string> = {
    user_message: "💬",
    llm_called: "🤖",
    agent_analysis: "🔍",
    kb_query: "📚",
    kb_mutation: "✏️",
    policy_check: "🔐",
    channel_created: "🔀",
    channel_message: "📨",
    channel_closed: "🔴",
    sentinel_alert: "⚠️",
    gbe_validation: "✅",
  };
  return icons[eventType] || "📍";
};

export const TraceVisualization: React.FC<TraceVisualizationProps> = ({ trace, loading, error, onRetry }) => {
  const [selectedNode, setSelectedNode] = useState<TraceNode | null>(null);

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
        {onRetry && <button onClick={onRetry}>Retry</button>}
      </div>
    );
  }

  if (!trace) {
    return <div className="trace-empty">No trace data</div>;
  }

  return (
    <div className="trace-visualization">
      <div className="trace-header">
        <h2>🔍 Trace: {trace.trace_id.slice(0, 8)}...</h2>
        <div className="trace-stats">
          <div className="stat">
            <strong>{trace.metadata.total_events}</strong>
            <span>Events</span>
          </div>
          <div className="stat">
            <strong>{trace.metadata.duration_ms.toFixed(0)}ms</strong>
            <span>Duration</span>
          </div>
          <div className="stat">
            <strong>{(trace.metadata.success_rate * 100).toFixed(0)}%</strong>
            <span>Success Rate</span>
          </div>
          <div className="stat">
            <strong>{trace.metadata.actors.length}</strong>
            <span>Actors</span>
          </div>
        </div>
      </div>

      <div className="trace-timeline">
        <div className="timeline-track">
          {trace.nodes.map((node, idx) => (
            <div key={node.id} className="timeline-item">
              <div
                className={`event-node event-${node.status} ${selectedNode?.id === node.id ? "selected" : ""}`}
                onClick={() => setSelectedNode(node)}
              >
                <div className="node-index">{idx + 1}</div>
                <div className="node-icon">{eventIcon(node.type)}</div>
                <div className="node-info">
                  <div className="node-type">{node.type}</div>
                  <div className="node-actor">{node.actor}</div>
                </div>
                <div className="node-time">{new Date(node.timestamp).toLocaleTimeString()}</div>
              </div>

              {idx < trace.edges.length && (
                <div className="timeline-connector">
                  <div className="connector-line"></div>
                  <div className="connector-label">{trace.edges[idx].label}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {selectedNode && (
        <div className="trace-details">
          <div className="details-header">
            <h3>Event Details</h3>
            <button onClick={() => setSelectedNode(null)}>✕</button>
          </div>

          <div className="details-content">
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
                <span className={`status-badge status-${selectedNode.status}`}>{selectedNode.status}</span>
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
};
