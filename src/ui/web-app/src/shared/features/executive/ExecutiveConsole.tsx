import { GlassPanel } from '@shared-ui/GlassPanel';
import { SovereignButton } from '@shared-ui/SovereignButton';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchJson, postJson } from '@web-src/shared/client';
import { AlertTriangle, CheckCircle, Fingerprint, Shield, ShieldAlert, XCircle } from 'lucide-react';
import { useState } from 'react';

interface QueueItem {
    id: string;
    title: string;
    description: string;
    risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
    status: 'PENDING' | 'SIGNED' | 'REJECTED';
    created_at: string;
    synthesis?: {
        overall_confidence: number;
        consensus_recommendations: string[];
        all_concerns: string[];
        agent_results: any[];
        sentinel_alerts: any[];
        mediation?: {
            analysis: string;
            confidence: number;
        };
    };
}

export function ExecutiveConsole() {
    const queryClient = useQueryClient();
    const [signingId, setSigningId] = useState<string | null>(null);
    const [rationale, setRationale] = useState<string>('');
    const [expandedItem, setExpandedItem] = useState<string | null>(null);

    const queueQuery = useQuery<{ queue: QueueItem[]; history: QueueItem[] }>({
        queryKey: ['executive-queue'],
        queryFn: () => fetchJson('/api/executive/queue'),
        refetchInterval: 3000 // Real-time polling
    });

    const signMutation = useMutation({
        mutationFn: (id: string) => postJson(`/api/governance/sign/${id}`, {
            action: 'APPROVE',
            rationale: rationale || 'Executive approval via Sovereign Console',
            human_id: 'owner'
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['executive-queue'] });
            setSigningId(null);
            setRationale('');
        }
    });

    const rejectMutation = useMutation({
        mutationFn: (id: string) => postJson(`/api/governance/sign/${id}`, {
            action: 'REJECT',
            rationale: rationale || 'Executive rejection via Sovereign Console',
            human_id: 'owner'
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['executive-queue'] });
            setRationale('');
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
                            <GlassPanel key={item.id} variant="glow" className="border-l-4 border-l-brand-primary/50 relative overflow-hidden group">
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

                                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 mb-4">
                                        <h4 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Confirmation Mirror</h4>
                                        <p className="text-slate-700 leading-relaxed font-medium whitespace-pre-wrap">
                                            {item.description}
                                        </p>
                                    </div>

                                    {/* Synthesis Intelligence Layer */}
                                    {item.synthesis && (
                                        <div className="mb-6 space-y-3">
                                            <div className="flex items-center justify-between px-1">
                                                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Agent Consensus & Intelligence Pulse</h4>
                                                <div className="flex items-center gap-1">
                                                    <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                                                        CONFIDENCE: {(item.synthesis.overall_confidence * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 gap-2">
                                                {/* Mediator Advice (Most Important) */}
                                                {item.synthesis.mediation && (
                                                    <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 shadow-sm relative overflow-hidden group/mediation">
                                                        <div className="absolute top-0 right-0 p-2 opacity-10">
                                                            <ShieldAlert className="w-8 h-8 text-indigo-600" />
                                                        </div>
                                                        <p className="text-xs font-bold text-indigo-900 leading-relaxed italic pr-8">
                                                            " {item.synthesis.mediation.analysis} "
                                                        </p>
                                                        <div className="mt-2 text-[9px] font-black text-indigo-400 uppercase tracking-tighter">— MEDIATOR AGENT CORE</div>
                                                    </div>
                                                )}

                                                <button
                                                    onClick={() => setExpandedItem(expandedItem === item.id ? null : item.id)}
                                                    className="w-full flex items-center justify-center gap-2 py-2 text-[10px] font-black text-slate-400 hover:text-brand-primary transition-colors border-t border-slate-100 mt-2"
                                                >
                                                    {expandedItem === item.id ? 'HIDE UNDERLYING ANALYSIS' : 'VIEW AGENT RATIONALE & SIGNALS'}
                                                </button>

                                                {expandedItem === item.id && (
                                                    <div className="animate-in slide-in-from-top-2 duration-300 space-y-4 pt-2">
                                                        {/* Agent Pulse Grid */}
                                                        <div className="grid grid-cols-2 gap-2">
                                                            {item.synthesis.agent_results?.map((res: any, idx: number) => (
                                                                <div key={idx} className="p-3 rounded-lg bg-white border border-slate-100 flex items-center gap-2">
                                                                    <div className={`w-2 h-2 rounded-full ${res.decision === 'APPROVE' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-rose-500'}`} />
                                                                    <span className="text-[10px] font-bold text-slate-600 truncate">{res.agent_id}</span>
                                                                </div>
                                                            ))}
                                                        </div>

                                                        {/* Sentinel Alerts */}
                                                        {item.synthesis.sentinel_alerts && item.synthesis.sentinel_alerts.length > 0 && (
                                                            <div className="p-3 rounded-lg bg-rose-50 border border-rose-100">
                                                                <div className="flex items-center gap-2 mb-2 text-rose-600">
                                                                    <AlertTriangle className="w-4 h-4" />
                                                                    <span className="text-[10px] font-black uppercase tracking-widest">Sentinel Security Pulses</span>
                                                                </div>
                                                                <div className="space-y-1">
                                                                    {item.synthesis.sentinel_alerts.map((alert: any, idx: number) => (
                                                                        <div key={idx} className="text-[10px] text-rose-800 font-medium bg-white/50 p-2 rounded-md">
                                                                            {alert.label || alert.message}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    <div className="mb-6 space-y-2">
                                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest px-1">Your Rationale (Strategic Context)</label>
                                        <textarea
                                            value={rationale}
                                            onChange={(e) => setRationale(e.target.value)}
                                            placeholder="Why are you making this decision? (This helps the system learn your intent)"
                                            className="w-full h-24 p-4 rounded-xl bg-white border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent transition-all resize-none shadow-inner"
                                        />
                                    </div>

                                    <div className="flex gap-4 items-center">
                                        <SovereignButton
                                            onClick={() => {
                                                setSigningId(item.id);
                                                setTimeout(() => signMutation.mutate(item.id), 800);
                                            }}
                                            disabled={signingId === item.id}
                                            variant="primary"
                                            className="flex-1"
                                            icon={signingId === item.id ? <CheckCircle className="w-5 h-5 animate-bounce" /> : <Fingerprint className="w-5 h-5" />}
                                            isLoading={signingId === item.id}
                                        >
                                            {signingId === item.id ? 'SIGNING...' : 'I CONFIRM SOVEREIGNTY'}
                                        </SovereignButton>

                                        <SovereignButton
                                            onClick={() => rejectMutation.mutate(item.id)}
                                            variant="danger"
                                            icon={<XCircle className="w-5 h-5" />}
                                        >
                                            REJECT
                                        </SovereignButton>
                                    </div>
                                </div>
                            </GlassPanel>
                        ))}
                    </div>
                </div>
            ) : (
                <GlassPanel variant="flat" className="flex flex-col items-center justify-center text-center space-y-3 h-40 border border-emerald-100/50">
                    <Shield className="w-8 h-8 text-emerald-200" />
                    <p className="text-slate-400 font-medium text-sm">No Pending Executive Actions</p>
                    <p className="text-slate-300 text-xs">System autonomous.</p>
                </GlassPanel>
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
                            <GlassPanel key={item.id} variant="flat" className="p-4 flex items-center justify-between !bg-white/40">
                                <div>
                                    <p className="text-sm font-bold text-slate-700">{item.title}</p>
                                    <p className="text-[10px] text-slate-400 font-mono">
                                        {item.status === 'SIGNED' ? 'Self-Signed' : 'Rejected'} • {new Date(item.created_at).toLocaleTimeString()}
                                    </p>
                                </div>
                                <span className={`px-2 py-1 rounded text-[10px] font-black uppercase ${item.status === 'SIGNED' ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'
                                    }`}>
                                    {item.status}
                                </span>
                            </GlassPanel>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
