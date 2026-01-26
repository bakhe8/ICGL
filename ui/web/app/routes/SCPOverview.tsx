
import { useCallback, useEffect, useState } from 'react';
import { MetricsGrid } from '../components/admin/Dashboard/MetricsGrid';

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
}

const SCPOverview = () => {
    const [stats, setStats] = useState<Stats | null>(null);

    const loadStats = useCallback(async () => {
        try {
            const baseUrl = 'http://127.0.0.1:8000';
            const [obsRes, chanRes] = await Promise.all([
                fetch(`${baseUrl}/observability/stats`),
                fetch(`${baseUrl}/channels/stats`)
            ]);
            setStats({
                observability: await obsRes.json(),
                channels: await chanRes.json()
            });
        } catch (e) {
            console.error(e);
        }
    }, []);

    useEffect(() => {
        let mounted = true;
        const init = async () => {
            if (mounted) await loadStats();
        };
        init();

        const interval = setInterval(loadStats, 5000);
        return () => {
            mounted = false;
            clearInterval(interval);
        }
    }, [loadStats]);

    if (!stats) return <div className="p-10 text-center animate-pulse text-slate-400">Loading metrics...</div>;

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Observability Stats */}
                <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col gap-4">
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Observability</h3>
                    <div className="flex flex-col gap-2">
                        <StatRow label="Total Events" value={stats.observability.total_events} />
                        <StatRow label="Active Traces" value={stats.observability.total_traces} />
                        <StatRow label="Sessions" value={stats.observability.total_sessions} />
                    </div>
                </div>

                {/* Channel Stats */}
                <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col gap-4">
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Channels</h3>
                    <div className="flex flex-col gap-2">
                        <StatRow label="Active Channels" value={stats.channels.active_channels} highlight="text-emerald-500" />
                        <StatRow label="Total Violations" value={stats.channels.total_violations} highlight="text-red-500" />
                        <StatRow label="Total Messages" value={stats.channels.total_messages} />
                    </div>
                </div>

                {/* System Health (Pseudo) */}
                <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col gap-4">
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Integrity</h3>
                    <div className="flex items-center justify-center p-4">
                        <div className="relative w-24 h-24">
                            <svg className="w-full h-full" viewBox="0 0 36 36">
                                <path className="text-slate-200" strokeWidth="3" fill="none" stroke="currentColor" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                <path className="text-indigo-600" strokeWidth="3" strokeDasharray="98, 100" strokeLinecap="round" fill="none" stroke="currentColor" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center font-black text-slate-800">98%</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="border-t border-slate-100 pt-8">
                <h3 className="text-sm font-bold text-slate-800 mb-4">Real-time Telemetry Snapshot</h3>
                <MetricsGrid status={null} /> {/* Passing null for skeleton state or full status if available */}
            </div>
        </div>
    );
};

const StatRow = ({ label, value, highlight }: { label: string, value: string | number, highlight?: string }) => (
    <div className="flex justify-between items-center py-1 border-b border-white/50">
        <span className="text-xs text-slate-500 font-medium">{label}</span>
        <strong className={`text-sm font-black ${highlight || 'text-slate-800'}`}>{value}</strong>
    </div>
);

export default SCPOverview;
