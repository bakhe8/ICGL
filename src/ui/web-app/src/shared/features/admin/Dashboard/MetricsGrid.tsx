import { Activity, Shield, UserCheck, Zap } from 'lucide-react';
import React from 'react';
import type { SystemStatus } from '../../../types';

interface MetricsGridProps {
    status: SystemStatus | null;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ status }) => {
    if (!status) return <div className="animate-pulse flex gap-4"><div className="h-32 bg-white/5 rounded-xl w-full"></div></div>;

    const getAlertColor = (level: string) => {
        if (level === 'CRITICAL') return 'text-red-400 bg-red-500/10 border-red-500/30';
        if (level === 'HIGH') return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    };

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Alert Level */}
            <div className={`glass-panel p-4 flex flex-col justify-between border ${getAlertColor(status.active_alert_level).split(' ')[2]}`}>
                <div className="flex justify-between items-start">
                    <span className="text-white/50 text-sm font-medium">Sentinel Status</span>
                    <Shield className={getAlertColor(status.active_alert_level).split(' ')[0]} size={20} />
                </div>
                <div className="mt-4">
                    <div className={`text-2xl font-bold ${getAlertColor(status.active_alert_level).split(' ')[0]}`}>
                        {status.active_alert_level}
                    </div>
                    <div className="text-xs text-white/30 mt-1">Real-time threat monitoring</div>
                </div>
            </div>

            {/* Drift Detection */}
            <div className="glass-panel p-4 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                    <span className="text-white/50 text-sm font-medium">Policy Drift</span>
                    <Activity className="text-blue-400" size={20} />
                </div>
                <div className="mt-4">
                    <div className="text-2xl font-bold text-white">
                        {status.telemetry.drift_detection_count}
                    </div>
                    <div className="text-xs text-white/30 mt-1">Drift events detected</div>
                </div>
            </div>

            {/* Latency */}
            <div className="glass-panel p-4 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                    <span className="text-white/50 text-sm font-medium">Core Latency</span>
                    <Zap className="text-yellow-400" size={20} />
                </div>
                <div className="mt-4">
                    <div className="text-2xl font-bold text-white">
                        {status.telemetry.last_latency_ms} ms
                    </div>
                    <div className="text-xs text-white/30 mt-1">Last inference cycle</div>
                </div>
            </div>

            {/* Human Pending */}
            <div className="glass-panel p-4 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                    <span className="text-white/50 text-sm font-medium">Pending Review</span>
                    <UserCheck className={status.waiting_for_human ? "text-purple-400" : "text-white/20"} size={20} />
                </div>
                <div className="mt-4">
                    <div className="text-2xl font-bold text-white">
                        {status.waiting_for_human ? "1" : "0"}
                    </div>
                    <div className="text-xs text-white/30 mt-1">Decisions awaiting signature</div>
                </div>
            </div>
        </div>
    );
};

export default MetricsGrid;
