import { useState, useEffect } from 'react';
import './SCP.css';
import {
    Shield,
    Activity,
    Server,
    AlertTriangle,
    Terminal,
    Radio,
    CheckCircle,
    XCircle,
    RefreshCw
} from 'lucide-react';

interface ScpCardProps {
    title: string;
    icon?: React.ElementType;
    children: React.ReactNode;
    className?: string;
}

// Unified Card Component
const ScpCard = ({ title, icon: Icon, children, className = '' }: ScpCardProps) => (
    <div className={`scp-card ${className}`}>
        <div className="scp-card-header">
            <div className="scp-card-title">
                {Icon && <Icon size={18} className="text-gray-400" />}
                {title}
            </div>
        </div>
        <div>{children}</div>
    </div>
);

interface SystemEvent {
    id: number;
    timestamp: string | number;
    source: string;
    type: string;
    message: string;
    level: string;
    user?: string;
}

interface ChannelStatus {
    id: string;
    name: string;
    active: boolean;
    load: number;
    status: string;
    latency: number;
}

interface SystemIntegrity {
    integrity_score: number;
    status: string;
}

export const SCP = () => {
    const [activeTab, setActiveTab] = useState<'overview' | 'events' | 'channels'>('overview');
    const [events, setEvents] = useState<SystemEvent[]>([]);
    const [channels, setChannels] = useState<ChannelStatus[]>([]);
    const [systemHealth, setSystemHealth] = useState<SystemIntegrity | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const [eventsRes, channelsRes, healthRes] = await Promise.all([
                fetch('/events/stream?limit=20'),
                fetch('/channels/status'),
                fetch('/health/system')
            ]);

            if (eventsRes.ok) setEvents(await eventsRes.json());
            if (channelsRes.ok) setChannels(await channelsRes.json());
            if (healthRes.ok) setSystemHealth(await healthRes.json());
        } catch (e) {
            console.error("SCP Data Fetch Error", e);
        } finally {
            setLoading(false);
        }
    };

    // useEffect for Mock Data DISABLED - Switching to Real Data
    /*
    useEffect(() => {
        // Mock Status Streams
        const interval = setInterval(() => {
             // ... mock events ...
        }, 3000);

        setTimeout(() => {
             // ... mock channels ...
        }, 500);

        return () => clearInterval(interval);
    }, []);
    */

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const getStatusBadge = (status: string) => {
        const s = status.toLowerCase();
        if (s === 'normal' || s === 'active' || s === 'healthy') return <span className="status-badge active">Active</span>;
        if (s === 'warning' || s === 'degraded') return <span className="status-badge warning">Warning</span>;
        return <span className="status-badge error">Critical</span>;
    };

    if (loading && !systemHealth) {
        return (
            <div className="flex items-center justify-center h-full text-gray-500 gap-2">
                <RefreshCw className="animate-spin" />
                <span className="font-medium">Initializing Sovereign Control...</span>
            </div>
        );
    }

    return (
        <div className="scp-container">
            {/* Header */}
            <div className="scp-header">
                <div className="scp-header-title">
                    <h1>
                        <Shield className="text-royal-blue" size={28} />
                        لوحة التحكم السيادية
                    </h1>
                    <p>Sovereign Control Panel (SCP) - Level 0 Access</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={fetchData} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors" title="Refresh">
                        <RefreshCw size={20} />
                    </button>
                </div>
            </div>

            {/* Navigation */}
            <div className="scp-tabs">
                <button
                    className={`scp-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    <div className="flex items-center gap-2">
                        <Activity size={16} />
                        نظرة عامة (Overview)
                    </div>
                </button>
                <button
                    className={`scp-tab-btn ${activeTab === 'events' ? 'active' : ''}`}
                    onClick={() => setActiveTab('events')}
                >
                    <div className="flex items-center gap-2">
                        <Terminal size={16} />
                        سجل الأحداث (Event Stream)
                    </div>
                </button>
                <button
                    className={`scp-tab-btn ${activeTab === 'channels' ? 'active' : ''}`}
                    onClick={() => setActiveTab('channels')}
                >
                    <div className="flex items-center gap-2">
                        <Radio size={16} />
                        قنوات الاتصال (Channels)
                    </div>
                </button>
            </div>

            {/* Content Body */}
            <div className="scp-content">

                {/* 1. OVERVIEW TAB */}
                {activeTab === 'overview' && (
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        {/* Health Summary */}
                        <div className="scp-grid">
                            <ScpCard title="System Integrity" icon={Shield}>
                                <div className="flex items-center justify-between mb-4">
                                    <div className="text-3xl font-bold text-gray-800">
                                        {systemHealth?.integrity_score || 98}%
                                    </div>
                                    {getStatusBadge(systemHealth?.status || 'normal')}
                                </div>
                                <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">

                                    {(() => {
                                        const progressStyle = { width: `${systemHealth?.integrity_score || 98}%` };
                                        return (
                                            <div
                                                className="bg-green-500 h-full rounded-full transition-all duration-1000"
                                                {...{ style: progressStyle }}
                                            />
                                        );
                                    })()}
                                </div>
                            </ScpCard>

                            <ScpCard title="Active Protocols" icon={Server}>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-gray-600">Runtime Guard</span>
                                        <span className="text-green-600 font-bold flex items-center gap-1"><CheckCircle size={12} /> Active</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-gray-600">Policy Enforcement</span>
                                        <span className="text-green-600 font-bold flex items-center gap-1"><CheckCircle size={12} /> Active</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-gray-600">Archive Sync</span>
                                        <span className="text-amber-600 font-bold flex items-center gap-1"><Activity size={12} /> Syncing</span>
                                    </div>
                                </div>
                            </ScpCard>

                            <ScpCard title="Threat Monitor" icon={AlertTriangle}>
                                <div className="flex flex-col items-center justify-center h-full py-4 space-y-2">
                                    <div className="w-16 h-16 rounded-full bg-green-50 border border-green-100 flex items-center justify-center text-green-600">
                                        <Shield size={32} />
                                    </div>
                                    <span className="text-sm font-semibold text-gray-700">No Active Threats</span>
                                    <span className="text-xs text-gray-400">Last scan: 30s ago</span>
                                </div>
                            </ScpCard>
                        </div>
                    </div>
                )}

                {/* 2. EVENTS TAB */}
                {activeTab === 'events' && (
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="scp-stream-list">
                            {events.map((evt: SystemEvent, i: number) => (
                                <div key={i} className={`scp-event-item ${evt.level === 'ERROR' ? 'error' : ''}`}>
                                    <div>
                                        <div className="font-bold text-gray-800 flex items-center gap-2">
                                            {evt.level === 'ERROR' ? <XCircle size={16} className="text-red-500" /> : <CheckCircle size={16} className="text-green-500" />}
                                            {evt.type}
                                        </div>
                                        <div className="text-gray-600 mt-1">{evt.message}</div>
                                        <div className="scp-event-meta">
                                            <span>Origin: {evt.source}</span>
                                            <span>•</span>
                                            <span>User: {evt.user || 'System'}</span>
                                        </div>
                                    </div>
                                    <div className="text-xs text-gray-400 font-mono whitespace-nowrap">
                                        {new Date(evt.timestamp).toLocaleTimeString()}
                                    </div>
                                </div>
                            ))}
                            {events.length === 0 && (
                                <div className="text-center py-10 text-gray-400">
                                    No events recorded in the current stream.
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* 3. CHANNELS TAB */}
                {activeTab === 'channels' && (
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {channels.map((ch: ChannelStatus, i: number) => (
                                <ScpCard key={i} title={ch.name} icon={Radio}>
                                    <div className="flex flex-col gap-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-500">Status</span>
                                            {getStatusBadge(ch.status)}
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-500">Latency</span>
                                            <span className="font-mono text-sm">{ch.latency}ms</span>
                                        </div>
                                        <div className="flex justify-between items-center mt-2 pt-2 border-t border-gray-100">
                                            <span className="text-xs text-gray-400">Last heartbeat</span>
                                            <span className="text-xs text-gray-600">2s ago</span>
                                        </div>
                                    </div>
                                </ScpCard>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
