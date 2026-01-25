
import { useState, useEffect } from 'react';
import { MetricsGrid } from './MetricsGrid';
import { ADRFeed } from './ADRFeed';
import type { SystemStatus, ADR } from '../../types';

export const DashboardContainer = () => {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [adrs, setAdrs] = useState<ADR[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            // Fetch Status
            const statusRes = await fetch('http://127.0.0.1:8000/status');
            const statusData = await statusRes.json();
            setStatus(statusData);

            // Fetch ADRs
            const adrRes = await fetch('http://127.0.0.1:8000/kb/adrs');
            const adrData = await adrRes.json();
            setAdrs(adrData);
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
            await fetch(`http://127.0.0.1:8000/kb/adr/${adrId}`, { method: 'DELETE' });
            setAdrs(prev => prev.filter(adr => adr.id !== adrId));
        } catch (error) {
            console.error('Dashboard delete error:', error);
        }
    };

    if (loading && !status) {
        return <div className="p-8 text-white/30 text-center animate-pulse">Loading Governance Data...</div>;
    }

    return (
        <div className="h-full flex flex-col gap-6 animate-enter overflow-hidden">
            {/* Top Row: System Metrics */}
            <div className="shrink-0">
                <h2 className="text-xl font-light text-white/80 mb-4 px-1">System Telemetry</h2>
                <MetricsGrid status={status} />
            </div>

            {/* Bottom Row: ADR Feed & Charts (Placeholder for now) */}
            <div className="flex-1 min-h-0 grid grid-cols-1lg:grid-cols-3 gap-6">
                {/* Main Feed */}
                <div className="lg:col-span-2 h-full min-h-0">
                    <ADRFeed adrs={adrs} onDelete={handleDeleteAdr} />
                </div>

                {/* Drift / Sentinel Visuals (Placeholder) */}
                <div className="hidden lg:block glass-panel p-6 flex items-center justify-center text-white/20 border-dashed border-2 border-white/5">
                    Sentinel Visualizer (Coming Soon)
                </div>
            </div>
        </div>
    );
};
