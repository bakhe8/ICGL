import { useState, useEffect } from 'react';
import { Shield, CheckCircle, AlertTriangle, Lock, RefreshCw } from 'lucide-react';

interface SentinelStatus {
    overall: string;
    integrity: number;
    active_protocols: number;
    threats_blocked: number;
    last_scan: string;
}

export const SentinelPanel = () => {
    const [status, setStatus] = useState<SentinelStatus | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchStatus = () => { // Removed async from definition, simplified
        setLoading(true);
        // Mock Data for "Luxurious" Demo
        // In real app, this would be a fetch call
        setTimeout(() => {
            const mockData: SentinelStatus = {
                overall: 'SECURE',
                integrity: 100,
                active_protocols: 12,
                threats_blocked: 0,
                last_scan: new Date().toISOString()
            };
            setStatus(mockData);
            setLoading(false);
        }, 800);
    };

    useEffect(() => {
        fetchStatus();
    }, []);

    if (loading) {
        return (
            <div className="p-6 flex items-center justify-center text-gray-400">
                <RefreshCw className="animate-spin mr-2" size={16} />
                <span className="text-xs font-mono">SCANNING...</span>
            </div>
        );
    }

    const isSecure = status?.overall === 'SECURE';

    return (
        <div className="h-full flex flex-col bg-white overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className={`p-6 border-b ${isSecure ? 'bg-emerald-50 border-emerald-100' : 'bg-red-50 border-red-100'}`}>
                <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-xl shadow-sm ${isSecure ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'}`}>
                        <Shield size={32} />
                    </div>
                    <div>
                        <h2 className={`text-xl font-bold ${isSecure ? 'text-emerald-800' : 'text-red-800'}`}>
                            {isSecure ? 'النظام آمن' : 'تحذير أمني'}
                        </h2>
                        <p className={`text-sm ${isSecure ? 'text-emerald-600' : 'text-red-600'}`}>Sentinel Active Protection</p>
                    </div>
                </div>
            </div>

            {/* Metrics */}
            <div className="p-6 grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
                    <div className="flex items-center gap-2 text-gray-500 mb-1 text-xs uppercase tracking-wider font-semibold">
                        <CheckCircle size={14} /> System Integrity
                    </div>
                    <div className="text-2xl font-bold text-gray-800">{status?.integrity}%</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
                    <div className="flex items-center gap-2 text-gray-500 mb-1 text-xs uppercase tracking-wider font-semibold">
                        <Lock size={14} /> Active Protocols
                    </div>
                    <div className="text-2xl font-bold text-gray-800">{status?.active_protocols}</div>
                </div>
            </div>

            {/* Status List */}
            <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-3">
                <h3 className="text-sm font-bold text-gray-700 mb-2">Security Checks</h3>

                <StatusItem label="Runtime Guard" status="active" />
                <StatusItem label="Policy Enforcer" status="active" />
                <StatusItem label="Access Control" status="active" />
                <StatusItem label="Network Filter" status="active" />
                <StatusItem label="Anomaly Detection" status="standby" />

            </div>

            {/* Footer Action */}
            <div className="p-4 border-t border-gray-100 bg-gray-50">
                <button
                    onClick={fetchStatus}
                    className="w-full py-3 bg-white border border-gray-200 rounded-lg text-sm font-semibold text-gray-600 hover:text-blue-600 hover:border-blue-200 shadow-sm transition-all"
                >
                    Run Full Diagnostic Scan
                </button>
            </div>
        </div>
    );
};

const StatusItem = ({ label, status }: { label: string, status: 'active' | 'warning' | 'standby' }) => {
    const config = {
        active: { icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-50', text: 'text-emerald-700' },
        warning: { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-50', text: 'text-amber-700' },
        standby: { icon: Lock, color: 'text-gray-400', bg: 'bg-gray-50', text: 'text-gray-500' }
    }[status];

    const Icon = config.icon;

    return (
        <div className="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
            <span className="font-medium text-gray-700 text-sm">{label}</span>
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-bold uppercase ${config.bg} ${config.text}`}>
                <Icon size={12} />
                {status}
            </div>
        </div>
    );
};
