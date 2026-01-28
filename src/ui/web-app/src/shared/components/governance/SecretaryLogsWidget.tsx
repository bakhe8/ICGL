import { useQuery } from '@tanstack/react-query';
import { Clock } from 'lucide-react';

type SecretaryLog = {
    timestamp: string;
    event: string;
    summary: string;
    priority: 'high' | 'medium' | 'normal';
    stakeholders: string[];
};

export function SecretaryLogsWidget({ extraLogs = [] }: { extraLogs?: any[] }) {

    // Proper Query Function
    const { data } = useQuery<{ logs: SecretaryLog[], status: string }>({
        queryKey: ['secretary-logs'],
        queryFn: async () => {
            const res = await fetch('/api/governance/timeline');
            if (!res.ok) throw new Error('Failed to fetch logs');
            const result = await res.json();
            // Map timeline events to secretary log format
            const events = result.timeline || [];
            return {
                logs: events.slice(0, 10).map((e: any) => ({
                    timestamp: e.timestamp,
                    event: e.type,
                    summary: e.label || e.payload?.message || 'System Event',
                    priority: e.severity === 'high' || e.severity === 'CRITICAL' ? 'high' : 'normal',
                    stakeholders: [e.source || 'system']
                })),
                status: 'SYNCED'
            };
        },
        refetchInterval: 5000,
        placeholderData: (prev) => prev ?? { logs: [], status: "جاري المزامنة مع المجلس... (Syncing)" },
        initialData: { logs: [], status: "جاري المزامنة مع المجلس... (Syncing)" }
    });

    const safeExtraLogs = extraLogs.map(e => ({
        timestamp: e.timestamp,
        event: e.type,
        summary: e.payload?.message || e.payload?.label || 'Real-time Event',
        priority: 'normal',
        stakeholders: ['LIVE']
    })) as SecretaryLog[];

    const historyLogs = (data.logs || []) as SecretaryLog[];
    const logs = [...safeExtraLogs, ...historyLogs].slice(0, 8); // Combine and limit
    const status = data.status || "جاري انتظار البيانات من السكرتارية... (Waiting for signal)";

    return (
        <div className="space-y-4">
            {logs.length === 0 ? (
                <div className="text-center py-8 text-white/50 bg-white/5 rounded-xl border border-white/5">
                    <Clock className="w-6 h-6 mx-auto mb-2 opacity-30" />
                    <p className="text-sm">{status}</p>
                </div>
            ) : (
                <div className="grid gap-3">
                    {logs.map((log, i) => (
                        <div key={i} className={`p-4 rounded-xl border flex gap-4 ${log.priority === 'high' ? 'bg-red-500/10 border-red-500/50' : 'bg-white/5 border-white/10'}`}>
                            <div className={`p-2 rounded-lg h-fit ${log.priority === 'high' ? 'bg-red-500 text-white' : 'bg-indigo-500/20 text-indigo-300'}`}>
                                {log.priority === 'high' ? '🚨' : '📝'}
                            </div>
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="font-mono text-[10px] text-white/40">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                    <span className="text-xs font-bold uppercase tracking-wider opacity-70">{log.event}</span>
                                </div>
                                <p className="font-bold text-sm leading-snug">{log.summary}</p>
                                <div className="flex gap-2 mt-2">
                                    {log.stakeholders.map((s, idx) => (
                                        <span key={idx} className="text-[9px] px-2 py-0.5 bg-white/10 rounded-full text-white/60">
                                            {s}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
