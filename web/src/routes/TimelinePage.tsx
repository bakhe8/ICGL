import { useQuery } from '@tanstack/react-query';
import { Activity, CircleDot, Clock, Filter, Search } from 'lucide-react';
import { listDecisions, listGovernanceTimeline, listProposals } from '../api/queries';
import type { GovernanceEvent } from '../api/types';
import { useSCPStream } from '../hooks/useSCPStream';

export default function TimelinePage() {
    const { timeline: liveTimeline } = useSCPStream();

    const timelineQuery = useQuery<{ timeline: GovernanceEvent[] }>({
        queryKey: ['gov-timeline'],
        queryFn: () => listGovernanceTimeline(),
        staleTime: 5_000,
    });

    const decisionsQuery = useQuery({
        queryKey: ['decisions'],
        queryFn: () => listDecisions(),
    });

    const proposalsQuery = useQuery({
        queryKey: ['proposals'],
        queryFn: () => listProposals(),
    });

    const historicalEvents = Array.isArray(timelineQuery.data?.timeline) ? timelineQuery.data.timeline : [];

    // Combine live and historical for a unified view
    // In a real app, you'd merge or prioritize one
    const allEvents = [...historicalEvents];

    return (
        <div className="space-y-6">
            <header className="glass rounded-3xl p-6 sm:p-8">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-brand-soft rounded-2xl">
                            <Clock className="w-8 h-8 text-brand-base" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-extrabold text-ink leading-tight">
                                سجل الحوكمة <span className="text-brand-base">· Timeline</span>
                            </h1>
                            <p className="text-sm text-slate-600 mt-1">تتبع تاريخ القرارات، المقترحات، وتحركات العملاء في الوقت الفعلي.</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <span className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-100">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            LIVE STREAM ACTIVE
                        </span>
                    </div>
                </div>
            </header>

            <section className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass rounded-3xl p-6 space-y-6">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <Activity className="w-5 h-5 text-brand-base" />
                            تسلسل الأحداث (SCP Ledger)
                        </h3>
                        <div className="flex gap-2">
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="بحث في السجلات..."
                                    className="pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-base/20 transition-all w-48"
                                />
                            </div>
                            <button className="p-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50">
                                <Filter className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {allEvents.length > 0 ? (
                            allEvents.map((event, idx) => (
                                <div
                                    key={event.id || idx}
                                    className="relative pl-8 pb-8 last:pb-0 group"
                                >
                                    {/* Timeline Line */}
                                    <div className="absolute left-3.5 top-0 bottom-0 w-px bg-slate-200 group-last:bottom-auto group-last:h-3.5" />

                                    {/* Timeline Dot */}
                                    <div className="absolute left-0 top-1.5 w-7 h-7 rounded-full bg-white border-2 border-brand-base grid place-items-center z-10">
                                        <CircleDot className="w-3.5 h-3.5 text-brand-base" />
                                    </div>

                                    <div className="p-4 rounded-2xl border border-slate-200 bg-white/70 hover:border-brand-base/30 hover:bg-white transition-all">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-xs font-bold uppercase tracking-wider text-brand-base">
                                                {event.type}
                                            </span>
                                            <span className="text-[11px] text-slate-400 font-mono">
                                                {new Date(event.timestamp).toLocaleString()}
                                            </span>
                                        </div>
                                        <p className="text-sm font-semibold text-ink mb-1">{event.label || 'Sovereign Action recorded'}</p>
                                        <div className="flex items-center gap-2">
                                            <span className="px-2 py-0.5 rounded bg-slate-100 text-[10px] text-slate-600 border border-slate-200">
                                                Source: {event.source || 'SYSTEM'}
                                            </span>
                                            {event.severity && (
                                                <span className={`px-2 py-0.5 rounded text-[10px] border ${event.severity === 'critical' ? 'bg-rose-50 text-rose-700 border-rose-100' :
                                                        event.severity === 'warn' ? 'bg-amber-50 text-amber-700 border-amber-100' :
                                                            'bg-emerald-50 text-emerald-700 border-emerald-100'
                                                    }`}>
                                                    {event.severity.toUpperCase()}
                                                </span>
                                            )}
                                        </div>
                                        {event.payload && (
                                            <pre className="mt-3 p-3 rounded-lg bg-slate-900 text-[11px] text-slate-300 font-mono overflow-x-auto">
                                                {JSON.stringify(event.payload, null, 2)}
                                            </pre>
                                        )}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                                <Clock className="w-12 h-12 mb-4 opacity-10" />
                                <p>لا توجد أحداث مسجلة في الخط الزمني بعد.</p>
                            </div>
                        )}
                    </div>
                </div>

                <aside className="space-y-6">
                    <div className="glass rounded-3xl p-6 space-y-4">
                        <h3 className="font-semibold text-ink">إحصائيات التدقيق</h3>
                        <div className="grid grid-cols-2 gap-3">
                            <StatCard title="Total Events" value={allEvents.length} />
                            <StatCard title="Decisions" value={decisionsQuery.data?.decisions?.length || 0} />
                            <StatCard title="Proposals" value={proposalsQuery.data?.proposals?.length || 0} />
                            <StatCard title="Drift Alerts" value="0" color="text-amber-600" />
                        </div>
                    </div>

                    <div className="glass rounded-3xl p-6 space-y-4">
                        <h3 className="font-semibold text-ink">Live Feed (Raw)</h3>
                        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                            {liveTimeline.map((e, i) => (
                                <div key={i} className="text-[10px] font-mono p-2 bg-slate-50 border rounded-lg border-slate-200">
                                    <span className="text-brand-base">[{new Date(e.time).toLocaleTimeString()}]</span> {e.label}
                                </div>
                            ))}
                            {liveTimeline.length === 0 && <p className="text-xs text-slate-400 italic">بانتظار أحداث جديدة...</p>}
                        </div>
                    </div>
                </aside>
            </section>
        </div>
    );
}

function StatCard({ title, value, color = "text-ink" }: { title: string; value: string | number; color?: string }) {
    return (
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
            <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">{title}</p>
            <p className={`text-xl font-bold ${color}`}>{value}</p>
        </div>
    );
}
