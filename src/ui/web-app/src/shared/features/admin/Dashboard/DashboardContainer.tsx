
import { useEffect, useState } from 'react';
import type { ADR } from '../../../../domains/desk/types';
import type { SystemStatus } from '../../../types';
import { ADRFeed } from './ADRFeed';
import { MetricsGrid } from './MetricsGrid';

import { deleteAdr, listAdrs } from '../../../../domains/desk/api';
import { fetchSystemStatus } from '../../../api/system';

export const DashboardContainer = () => {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [adrs, setAdrs] = useState<ADR[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            // Fetch Status
            const statusData = await fetchSystemStatus();
            setStatus(statusData);

            // Fetch ADRs
            const adrData = await listAdrs();
            setAdrs(adrData.adrs || []);
        } catch (error) {
            console.error('Dashboard fetch error:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Poll every 5 seconds for live updates
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleDeleteAdr = async (adrId: string) => {
        const confirmed = window.confirm(`Delete ADR ${adrId}? This cannot be undone.`);
        if (!confirmed) return;
        try {
            await deleteAdr(adrId);
            setAdrs(prev => prev.filter(adr => adr.id !== adrId));
        } catch (error) {
            console.error('Dashboard delete error:', error);
        }
    };

    if (loading && !status) {
        return <div className="p-8 text-slate-400 text-center animate-pulse">Loading Governance Data...</div>;
    }

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700 overflow-hidden">
            {/* Top Row: System Metrics */}
            <div className="shrink-0">
                <h2 className="text-xl font-bold text-slate-800 mb-4 px-1">System Telemetry | القياسات الحيوية للنظام</h2>
                <MetricsGrid status={status} />
            </div>

            {/* Bottom Row: ADR Feed */}
            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Feed */}
                <div className="lg:col-span-2 h-full min-h-0">
                    <ADRFeed adrs={adrs} onDelete={handleDeleteAdr} />
                </div>

                {/* Drift / Sentinel Visuals (Placeholder) */}
                <div className="hidden lg:block rounded-2xl p-6 flex items-center justify-center text-slate-300 border-dashed border-2 border-slate-200 bg-white/50 backdrop-blur-sm">
                    Sentinel Visualizer (Coming Soon)
                </div>
            </div>
        </div>
    );
};

export default DashboardContainer;
