import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchJson, postJson } from '@web-src/client'; // Adjust path as needed
import { AlertTriangle, CheckCircle, Fingerprint, Shield, XCircle } from 'lucide-react';
import { useState } from 'react';

interface QueueItem {
    id: string;
    title: string;
    description: string;
    risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
    status: 'PENDING' | 'SIGNED' | 'REJECTED';
    created_at: string;
}

export function ExecutiveConsole() {
    const queryClient = useQueryClient();
    const [signingId, setSigningId] = useState<string | null>(null);

    const queueQuery = useQuery<{ queue: QueueItem[]; history: QueueItem[] }>({
        queryKey: ['executive-queue'],
        queryFn: () => fetchJson('/api/executive/queue'),
        refetchInterval: 3000 // Real-time polling
    });

    const signMutation = useMutation({
        mutationFn: (id: string) => postJson(`/api/executive/sign/${id}`, { human_id: 'owner' }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['executive-queue'] });
            setSigningId(null);
        }
    });

    const rejectMutation = useMutation({
        mutationFn: (id: string) => postJson(`/api/executive/reject/${id}`, { human_id: 'owner' }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['executive-queue'] });
        }
    });

    const pendingItems = queueQuery.data?.queue.filter((q: QueueItem) => q.status === 'PENDING') || [];
    const historyItems = queueQuery.data?.history || [];

    return (
        <div className="space-y-8">
            {/* Pending Items Section */}
            {pendingItems.length > 0 ? (
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                            <Fingerprint className="w-5 h-5 text-brand-primary" />
                            Executive Signing Queue
                            <span className="bg-rose-100 text-rose-600 px-2 py-0.5 rounded-full text-xs font-black animate-pulse">
                                {pendingItems.length} ACTION REQUIRED
                            </span>
                        </h2>
                    </div>

                    <div className="space-y-4">
                        {pendingItems.map((item: QueueItem) => (
                            <div key={item.id} className="glass-panel p-6 rounded-2xl border-l-4 border-l-brand-primary/50 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                                    <Fingerprint className="w-32 h-32 text-brand-primary" />
                                </div>

                                <div className="relative z-10">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-xl font-bold text-slate-800">{item.title}</h3>
                                            <p className="text-xs text-slate-400 font-mono mt-1">ID: {item.id} • RISK: {item.risk_level}</p>
                                        </div>
                                        <div className="p-2 bg-rose-50 rounded-full text-rose-500">
                                            <AlertTriangle className="w-6 h-6" />
                                        </div>
                                    </div>

                                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 mb-6">
                                        <h4 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Confirmation Mirror</h4>
                                        <p className="text-slate-700 leading-relaxed font-medium whitespace-pre-wrap">
                                            {item.description}
                                        </p>
                                    </div>

                                    <div className="flex gap-4 items-center">
                                        <button
                                            onClick={() => {
                                                setSigningId(item.id);
                                                setTimeout(() => signMutation.mutate(item.id), 800);
                                            }}
                                            disabled={signingId === item.id}
                                            className={`flex-1 group relative overflow-hidden rounded-xl py-4 font-black transition-all
                                                ${signingId === item.id
                                                    ? 'bg-emerald-500 text-white scale-95'
                                                    : 'bg-brand-primary text-white hover:bg-brand-deep shadow-lg hover:shadow-brand-primary/25'
                                                }`}
                                        >
                                            <div className="flex items-center justify-center gap-3 relative z-10">
                                                {signingId === item.id ? (
                                                    <>
                                                        <CheckCircle className="w-5 h-5 animate-bounce" />
                                                        SIGNING...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Fingerprint className="w-5 h-5 group-hover:scale-110 transition-transform" />
                                                        I CONFIRM SOVEREIGNTY
                                                    </>
                                                )}
                                            </div>
                                            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                                        </button>

                                        <button
                                            onClick={() => rejectMutation.mutate(item.id)}
                                            className="px-6 py-4 rounded-xl bg-slate-100 text-slate-500 font-bold hover:bg-rose-100 hover:text-rose-600 transition-colors"
                                        >
                                            <XCircle className="w-6 h-6" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="glass-panel p-6 rounded-2xl flex flex-col items-center justify-center text-center space-y-3 h-40 border border-emerald-100/50">
                    <Shield className="w-8 h-8 text-emerald-200" />
                    <p className="text-slate-400 font-medium text-sm">No Pending Executive Actions</p>
                    <p className="text-slate-300 text-xs">System autonomous.</p>
                </div>
            )}

            {/* History Section */}
            {historyItems.length > 0 && (
                <div className="opacity-70 hover:opacity-100 transition-opacity">
                    <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <CheckCircle className="w-3 h-3" />
                        Executive Log (Recent)
                    </h3>
                    <div className="space-y-3">
                        {historyItems.map((item: QueueItem) => (
                            <div key={item.id} className="flex items-center justify-between p-4 rounded-xl bg-white/40 border border-slate-100">
                                <div>
                                    <p className="text-sm font-bold text-slate-700">{item.title}</p>
                                    <p className="text-[10px] text-slate-400 font-mono">
                                        {item.status === 'SIGNED' ? 'Self-Signed' : 'Rejected'} • {new Date(item.created_at).toLocaleTimeString()}
                                    </p>
                                </div>
                                <span className={`px-2 py-1 rounded text-[10px] font-black uppercase
                                    ${item.status === 'SIGNED' ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'}`}>
                                    {item.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
