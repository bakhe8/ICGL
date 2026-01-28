
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchJson, postJson } from '@web-src/shared/client';
import { AlertTriangle, Power, X } from 'lucide-react';
import { useState } from 'react';

const AgentDetailsModal = ({
    agent,
    events,
    onClose
}: {
    agent: string;
    events: Array<{ time: string; description: string; confidence?: number; verdict?: string }>;
    onClose: () => void;
}) => {
    const queryClient = useQueryClient();
    const [confirmKill, setConfirmKill] = useState(false);

    // 1. Fetch current status
    // 1. Fetch current status
    const statusQuery = useQuery({
        queryKey: ['agent-status', agent],
        queryFn: async () => {
            return fetchJson<{ status: string }>(`/api/system/agents/${agent}/status`);
        },
        refetchInterval: 2000 // Poll for status changes
    });

    const lifecycleMutation = useMutation({
        mutationFn: async ({ action, reason }: { action: 'kill' | 'revive'; reason: string }) => {
            return postJson(`/api/system/agents/${agent}/lifecycle`, {
                action,
                reason,
                operator: 'bakheet' // Hardcoded owner for now
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agents-registry'] });
            onClose();
        }
    });

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-3xl p-6 min-w-[320px] max-w-2xl w-full shadow-2xl space-y-6">

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-black text-white flex items-center gap-3">
                            {agent}
                            <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-400 font-mono">ID: {agent}</span>
                        </h2>
                        <p className="text-slate-500 text-sm">Agent Diagnostics & Control</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                {/* Lifecycle Switch Area (Policy DRA-P01) */}
                <div className={`p-4 rounded-2xl border space-y-4 ${statusQuery.data?.status === 'suspended' ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-rose-500/5 border-rose-500/20'}`}>
                    <div className="flex items-center gap-3">
                        <div className={`p-3 rounded-full ${statusQuery.data?.status === 'suspended' ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
                            <Power className={`w-6 h-6 ${statusQuery.data?.status === 'suspended' ? 'text-emerald-500' : 'text-rose-500'}`} />
                        </div>
                        <div>
                            <h3 className={`font-bold ${statusQuery.data?.status === 'suspended' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {statusQuery.data?.status === 'suspended' ? 'إعادة التفعيل (Revival Protocol)' : 'بروتوكول الإيقاف القسري (Kill Switch)'}
                            </h3>
                            <p className={`text-xs ${statusQuery.data?.status === 'suspended' ? 'text-emerald-500/60' : 'text-rose-500/60'}`}>
                                صلاحية حصرية للمالك (Owner Authority)
                            </p>
                        </div>
                    </div>

                    {!confirmKill ? (
                        <button
                            onClick={() => setConfirmKill(true)}
                            className={`w-full py-3 rounded-xl font-bold transition-all shadow-lg ${statusQuery.data?.status === 'suspended'
                                ? 'bg-emerald-600 hover:bg-emerald-700 text-white hover:shadow-emerald-500/20'
                                : 'bg-rose-600 hover:bg-rose-700 text-white hover:shadow-rose-500/20'
                                }`}
                        >
                            {statusQuery.data?.status === 'suspended' ? 'إعادة تفعيل الوكيل (Revive Agent)' : 'إيقاف الوكيل فوراً (Suspend Agent)'}
                        </button>
                    ) : (
                        <div className="space-y-3 animate-in fade-in slide-in-from-top-2">
                            <div className={`flex items-start gap-2 text-xs p-3 rounded-lg ${statusQuery.data?.status === 'suspended' ? 'bg-emerald-950/30 text-emerald-300' : 'bg-rose-950/30 text-rose-300'}`}>
                                <AlertTriangle className="w-4 h-4 shrink-0" />
                                <p>
                                    {statusQuery.data?.status === 'suspended'
                                        ? 'سيتم إعادة الوكيل للعمل والسماح له باتخاذ القرارات مجدداً.'
                                        : 'تحذير: هذا الإجراء سيوقف جميع عمليات الوكيل وسيمنعه من المشاركة في أي تصويت أو قرار حتى يتم تفعيله يدوياً.'}
                                </p>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <button
                                    onClick={() => setConfirmKill(false)}
                                    className="py-3 rounded-xl bg-slate-800 text-slate-300 font-bold hover:bg-slate-700 transition-colors"
                                >
                                    إلغاء
                                </button>
                                <button
                                    onClick={() => lifecycleMutation.mutate({
                                        action: statusQuery.data?.status === 'suspended' ? 'revive' : 'kill',
                                        reason: 'Owner manual override'
                                    })}
                                    className={`py-3 rounded-xl text-white font-black transition-colors flex items-center justify-center gap-2 ${statusQuery.data?.status === 'suspended' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-rose-600 hover:bg-rose-700'
                                        }`}
                                >
                                    {lifecycleMutation.isPending ? 'جاري التنفيذ...' : (statusQuery.data?.status === 'suspended' ? 'تأكيد التفعيل 🟢' : 'تأكيد الإيقاف 💀')}
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Event Log */}
                <div className="space-y-2">
                    <h4 className="font-bold text-white text-sm">سجل التشغيل الأخير</h4>
                    <div className="max-h-[200px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                        {events.map((ev, idx) => (
                            <div key={idx} className="bg-slate-800/50 p-3 rounded-xl border border-slate-700/50">
                                <div className="flex justify-between items-start">
                                    <span className="text-slate-300 text-sm font-medium">{ev.description}</span>
                                    <span className="text-slate-500 text-[10px] font-mono">{ev.time}</span>
                                </div>
                                {ev.confidence && (
                                    <div className="mt-1 flex items-center gap-2">
                                        <div className="h-1 bg-slate-700 w-16 rounded-full overflow-hidden">
                                            <div className="h-full bg-brand-primary" style={{ width: `${ev.confidence * 100}%` }} />
                                        </div>
                                        <span className="text-[9px] text-slate-400">{Math.round(ev.confidence * 100)}% confidence</span>
                                    </div>
                                )}
                            </div>
                        ))}
                        {events.length === 0 && (
                            <div className="text-center py-8 text-slate-600 text-sm">لا توجد سجلات حديثة</div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default AgentDetailsModal;
