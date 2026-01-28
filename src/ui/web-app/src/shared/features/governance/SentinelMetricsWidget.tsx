import { useQuery } from '@tanstack/react-query';
import { Activity, Database, ShieldCheck, Zap } from 'lucide-react';
import { useState } from 'react';
import { fetchJson } from '../../client';

type SentinelMetrics = {
    status: string;
    semantic_memory_size: string;
    active_policies: number;
    recent_alerts: any[];
};

export function SentinelMetricsWidget() {
    const [metrics, setMetrics] = useState<SentinelMetrics | null>(null);

    const fetchMetrics = async () => {
        try {
            const data = await fetchJson<any>('/api/system/sentinel-metrics');
            if (data) {
                setMetrics(data);
            }
        } catch (e) {
            console.error("Failed to fetch sentinel metrics", e);
        }
    };

    useQuery({
        queryKey: ['sentinel-metrics'],
        queryFn: fetchMetrics,
        refetchInterval: 10000
    });

    if (!metrics) return (
        <div className="p-6 text-center text-slate-400 animate-pulse">
            Connecting to Sentinel Core...
        </div>
    );

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard icon={<Activity className="w-5 h-5 text-emerald-500" />} label="System Status" value={metrics.status.toUpperCase()} />
            <MetricCard icon={<ShieldCheck className="w-5 h-5 text-indigo-500" />} label="Active Policies" value={metrics.active_policies} />
            <MetricCard icon={<Database className="w-5 h-5 text-blue-500" />} label="Memory Interface" value={metrics.semantic_memory_size} />
            <MetricCard icon={<Zap className="w-5 h-5 text-amber-500" />} label="Threat Level" value="LOW" subtext="No active drifts" />
        </div>
    );
}

function MetricCard({ icon, label, value, subtext }: { icon: any, label: string, value: string | number, subtext?: string }) {
    return (
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4 hover:shadow-md transition-all">
            <div className="bg-slate-50 p-3 rounded-lg">
                {icon}
            </div>
            <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wide">{label}</p>
                <p className="text-xl font-black text-slate-900">{value}</p>
                {subtext && <p className="text-[10px] text-emerald-600 font-bold">{subtext}</p>}
            </div>
        </div>
    );
}
