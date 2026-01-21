import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { TraceVisualization } from '../components/TraceVisualization';
import { PolicyEditor } from '../components/PolicyEditor';
import { Chat } from '../components/Chat';
import './SCP.css';

/**
 * Sovereign Control Panel (SCP)
 * 
 * Real-time monitoring and control dashboard for supervised swarm intelligence.
 * 
 * Features:
 * - Live event stream
 * - Active channel monitoring
 * - System health metrics
 * - Pattern detection alerts
 * - Emergency controls
 */

interface Alert {
    alert_id: string;
    severity: string;
    pattern: string;
    description: string;
}

interface ObservabilityEvent {
    event_type: string;
    actor_id: string;
    action: string;
    status: string;
    timestamp: string;
    target?: string;
    error_message?: string;
}

interface Channel {
    channel_id: string;
    from_agent: string;
    to_agent: string;
    status: string;
    message_count: number;
    violation_count: number;
    policy?: { name: string };
}

interface Stats {
    observability: {
        total_events: number;
        total_traces: number;
        total_sessions: number;
    };
    channels: {
        active_channels: number;
        closed_channels: number;
        total_messages: number;
        total_violations: number;
    };
    patterns?: {
        alerts: Alert[];
        count: number;
    };
}

export default function SCP() {
    const [activeTab, setActiveTab] = useState<'overview' | 'events' | 'channels' | 'traces' | 'policies' | 'chat'>('overview');
    const [stats, setStats] = useState<Stats>({
        observability: { total_events: 0, total_traces: 0, total_sessions: 0 },
        channels: { active_channels: 0, closed_channels: 0, total_messages: 0, total_violations: 0 }
    });
    const [events, setEvents] = useState<ObservabilityEvent[]>([]);
    const [channels, setChannels] = useState<Channel[]>([]);
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);

    const { lastMessage } = useWebSocket('ws://127.0.0.1:8000/ws/scp');

    const loadStats = useCallback(async () => {
        try {
            const [obsRes, chanRes, alertsRes] = await Promise.all([
                fetch('http://127.0.0.1:8000/observability/stats'),
                fetch('http://127.0.0.1:8000/channels/stats'),
                fetch('http://127.0.0.1:8000/patterns/alerts?limit=5')
            ]);

            const obs = await obsRes.json();
            const chan = await chanRes.json();
            const alertsData = await alertsRes.json();

            setStats({ observability: obs, channels: chan, patterns: alertsData });
            setAlerts(alertsData.alerts || []);

            // Load channels list
            if (activeTab === 'channels') {
                const channelsRes = await fetch('http://127.0.0.1:8000/channels');
                const channelsData = await channelsRes.json();
                setChannels(channelsData.channels || []);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }, [activeTab]);

    // Load initial stats
    useEffect(() => {
        loadStats();
        const interval = setInterval(loadStats, 5000); // Refresh every 5s
        return () => clearInterval(interval);
    }, [loadStats]);

    // Handle WebSocket messages
    useEffect(() => {
        if (!lastMessage) return;

        if (lastMessage.type === 'event') {
            setEvents(prev => [lastMessage.data as ObservabilityEvent, ...prev].slice(0, 100));
        } else if (lastMessage.type === 'channel_update') {
            setChannels(prev => {
                const data = lastMessage.data as Channel;
                const idx = prev.findIndex(c => c.channel_id === data.channel_id);
                if (idx >= 0) {
                    const updated = [...prev];
                    updated[idx] = { ...updated[idx], ...data };
                    return updated;
                }
                return prev;
            });
        }
    }, [lastMessage]);

    const runPatternDetection = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/patterns/detect', { method: 'POST' });
            const result = await res.json();
            alert(`Pattern Detection Complete\n\nAnalyzed: ${result.analyzed_events} events\nAlerts: ${result.alerts_found}`);
            loadStats();
        } catch (error) {
            console.error('Pattern detection failed:', error);
        }
    };

    const terminateChannel = async (channelId: string) => {
        if (!confirm('Emergency terminate this channel?')) return;

        try {
            await fetch(`http://127.0.0.1:8000/channels/${channelId}/terminate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason: 'Human emergency shutdown' })
            });
            alert('Channel terminated');
            loadStats();
        } catch (error) {
            console.error('Termination failed:', error);
        }
    };

    return (
        <div className="scp-container">
            {/* Header */}
            <div className="scp-header">
                <h1>🎛️ Sovereign Control Panel</h1>
                <div className="scp-status">
                    <span className="status-indicator active"></span>
                    <span>System Online</span>
                </div>
            </div>

            {/* Alerts Banner */}
            {alerts.length > 0 && (
                <div className="alerts-banner">
                    <strong>⚠️ {alerts.length} Active Alerts</strong>
                    {alerts.map(alert => (
                        <div key={alert.alert_id} className={`alert alert-${alert.severity}`}>
                            <strong>{alert.pattern}</strong>: {alert.description}
                        </div>
                    ))}
                </div>
            )}

            {/* Tabs */}
            <div className="scp-tabs">
                <button
                    className={activeTab === 'overview' ? 'active' : ''}
                    onClick={() => setActiveTab('overview')}
                >
                    📊 Overview
                </button>
                <button
                    className={activeTab === 'events' ? 'active' : ''}
                    onClick={() => setActiveTab('events')}
                >
                    📡 Events
                </button>
                <button
                    className={activeTab === 'channels' ? 'active' : ''}
                    onClick={() => setActiveTab('channels')}
                >
                    🔀 Channels
                </button>
                <button
                    className={activeTab === 'traces' ? 'active' : ''}
                    onClick={() => setActiveTab('traces')}
                >
                    🔍 Traces
                </button>
                <button
                    className={`tab ${activeTab === 'policies' ? 'active' : ''}`}
                    onClick={() => setActiveTab('policies')}
                >
                    📋 Policies
                </button>
                <button
                    className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
                    onClick={() => setActiveTab('chat')}
                >
                    💬 Chat
                </button>
            </div>

            {/* Content */}
            <div className="scp-content">
                {activeTab === 'overview' && (
                    <div className="overview-grid">
                        {/* Observability Stats */}
                        <div className="stat-card">
                            <h3>📊 Observability</h3>
                            <div className="stat-row">
                                <span>Total Events:</span>
                                <strong>{stats.observability.total_events}</strong>
                            </div>
                            <div className="stat-row">
                                <span>Traces:</span>
                                <strong>{stats.observability.total_traces}</strong>
                            </div>
                            <div className="stat-row">
                                <span>Sessions:</span>
                                <strong>{stats.observability.total_sessions}</strong>
                            </div>
                        </div>

                        {/* Channel Stats */}
                        <div className="stat-card">
                            <h3>🔀 Channels</h3>
                            <div className="stat-row">
                                <span>Active:</span>
                                <strong className="text-success">{stats.channels.active_channels}</strong>
                            </div>
                            <div className="stat-row">
                                <span>Total Messages:</span>
                                <strong>{stats.channels.total_messages}</strong>
                            </div>
                            <div className="stat-row">
                                <span>Violations:</span>
                                <strong className="text-danger">{stats.channels.total_violations}</strong>
                            </div>
                        </div>

                        {/* Patterns */}
                        <div className="stat-card">
                            <h3>🔍 Pattern Detection</h3>
                            <div className="stat-row">
                                <span>Active Alerts:</span>
                                <strong className={alerts.length > 0 ? 'text-warning' : ''}>{alerts.length}</strong>
                            </div>
                            <button onClick={runPatternDetection} className="btn-primary">
                                Run Detection
                            </button>
                        </div>

                        {/* Emergency Controls */}
                        <div className="stat-card emergency-card">
                            <h3>🚨 Emergency Controls</h3>
                            <button className="btn-danger" onClick={() => alert('Emergency stop: Not implemented')}>
                                Emergency Stop All
                            </button>
                            <button className="btn-warning" onClick={loadStats}>
                                Refresh Stats
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'events' && (
                    <div className="events-stream">
                        <div className="stream-header">
                            <h3>📡 Real-Time Event Stream</h3>
                            <span className="event-count">{events.length} events loaded</span>
                        </div>
                        <div className="events-list">
                            {events.length === 0 && (
                                <div className="empty-state">
                                    <p>No events yet. Waiting for system activity...</p>
                                    <small>Events will appear here in real-time</small>
                                </div>
                            )}
                            {events.map((event, idx) => (
                                <div key={idx} className={`event-item event-${event.status}`}>
                                    <div className="event-header">
                                        <span className="event-type">{event.event_type}</span>
                                        <span className="event-time">{new Date(event.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    <div className="event-details">
                                        <span><strong>Actor:</strong> {event.actor_id}</span>
                                        <span><strong>Action:</strong> {event.action}</span>
                                        {event.target && <span><strong>Target:</strong> {event.target}</span>}
                                    </div>
                                    {event.error_message && (
                                        <div className="event-error">❌ {event.error_message}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'channels' && (
                    <div className="channels-monitor">
                        <div className="stream-header">
                            <h3>🔀 Active Channels</h3>
                            <button onClick={loadStats} className="btn-secondary">Refresh</button>
                        </div>
                        <div className="channels-list">
                            {channels.length === 0 && (
                                <div className="empty-state">
                                    <p>No active channels</p>
                                    <small>Channels will appear when agents coordinate</small>
                                </div>
                            )}
                            {channels.map(channel => (
                                <div key={channel.channel_id} className="channel-card">
                                    <div className="channel-header">
                                        <h4>{channel.from_agent} → {channel.to_agent}</h4>
                                        <span className={`channel-status status-${channel.status}`}>
                                            {channel.status}
                                        </span>
                                    </div>
                                    <div className="channel-stats">
                                        <div className="channel-stat">
                                            <span>Messages:</span>
                                            <strong>{channel.message_count}</strong>
                                        </div>
                                        <div className="channel-stat">
                                            <span>Violations:</span>
                                            <strong className={channel.violation_count > 0 ? 'text-danger' : ''}>
                                                {channel.violation_count}
                                            </strong>
                                        </div>
                                        <div className="channel-stat">
                                            <span>Policy:</span>
                                            <strong>{channel.policy?.name || 'Unknown'}</strong>
                                        </div>
                                    </div>
                                    {channel.status === 'active' && (
                                        <button
                                            onClick={() => terminateChannel(channel.channel_id)}
                                            className="btn-danger btn-sm"
                                        >
                                            🚨 Terminate
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'traces' && (
                    <div className="traces-view">
                        <div className="stream-header">
                            <h3>🔍 Trace Visualization</h3>
                            {stats.observability.total_traces > 0 && (
                                <span>{stats.observability.total_traces} traces available</span>
                            )}
                        </div>
                        {selectedTraceId ? (
                            <div>
                                <button
                                    onClick={() => setSelectedTraceId(null)}
                                    className="btn-secondary"
                                    style={{ marginBottom: '1rem' }}
                                >
                                    ← Back
                                </button>
                                <TraceVisualization traceId={selectedTraceId} />
                            </div>
                        ) : (
                            <div className="empty-state">
                                <p>Enter a trace ID to visualize</p>
                                <input
                                    type="text"
                                    placeholder="trace_abc123..."
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                            const input = e.target as HTMLInputElement;
                                            if (input.value) setSelectedTraceId(input.value);
                                        }
                                    }}
                                    style={{
                                        width: '100%',
                                        maxWidth: '500px',
                                        padding: '0.75rem',
                                        background: 'rgba(255,255,255,0.05)',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '6px',
                                        color: '#e0e0e0',
                                        fontSize: '1rem',
                                        marginTop: '1rem'
                                    }}
                                />
                                <small style={{ color: '#888', marginTop: '0.5rem', display: 'block' }}>
                                    Press Enter to load
                                </small>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'policies' && (
                    <PolicyEditor />
                )}

                {activeTab === 'chat' && (
                    <Chat />
                )}
            </div>
        </div>
    );
}
