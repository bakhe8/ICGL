/* eslint-disable @typescript-eslint/no-explicit-any */
import { useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { fetchAgentGaps, getLatestAdr } from '../../queries';
import type { AgentInfo } from './AgentCard';
import AgentCard from './AgentCard';
import AgentDetailsModal from './AgentDetailsModal';
import { fetchAgentHistory, fetchAgents, fetchAgentStats, fetchEvents, fetchIdeaSummary, fetchLatestAnalysis, fetchStatus } from './api';
import type { EventInfo } from './EventLog';
import EventLog from './EventLog';
import IdeaSummary from './IdeaSummary';
import StatusIndicators from './StatusIndicators';
import WorkflowBoard from './WorkflowBoard';

const AgentsFlowPage = () => {
    const [adrId, setAdrId] = useState<string | null>(null);
    const [agents, setAgents] = useState<AgentInfo[]>([]);
    const [stages, setStages] = useState<any[]>([]);
    const [events, setEvents] = useState<EventInfo[]>([]);
    const [status, setStatus] = useState<string>('');
    const [idea, setIdea] = useState<string>('');
    const [summary, setSummary] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [detailsAgent, setDetailsAgent] = useState<string | null>(null);
    const [detailsEvents, setDetailsEvents] = useState<EventInfo[]>([]);
    const [agentStats, setAgentStats] = useState<Record<string, any>>({});
    const [gaps, setGaps] = useState<{ critical: any[]; medium: any[]; enhancement: any[] }>({
        critical: [],
        medium: [],
        enhancement: [],
    });

    // Fetch the latest ADR to bind analysis view
    useQuery({
        queryKey: ['latest-adr-id'],
        queryFn: async () => {
            const latest = await getLatestAdr();
            if ((latest as any)?.id) setAdrId((latest as any).id);
            return latest;
        },
        refetchOnWindowFocus: false,
    });

    useEffect(() => {
        async function loadGeneralData() {
            setLoading(true);
            try {
                const [agentsData, eventsData, statusData] = await Promise.all([
                    fetchAgents(),
                    fetchEvents(),
                    fetchStatus(),
                ]);
                setAgents(
                    agentsData.map((a: any) => ({
                        id: a.id || a.name,
                        name: a.name,
                        role: a.role,
                        status: a.status,
                        lastTask: a.lastTask || '',
                        recommendation: a.recommendation || '',
                    })),
                );

                const normalizedEvents = Array.isArray(eventsData?.events)
                    ? eventsData.events.map((e: any) => ({
                        time: e.timestamp || '',
                        agent: e.user_id || e.trace_id || 'system',
                        description: e.message || e.payload?.message || e.type || '',
                        type: (e.type || e.event_type || 'info').toLowerCase(),
                    }))
                    : Array.isArray(eventsData) ? eventsData : [];
                setEvents(normalizedEvents);
                setStatus(statusData.status || '');

                if (adrId) {
                    const [latestAnalysis, ideaSummaryData] = await Promise.all([
                        fetchLatestAnalysis(),
                        fetchIdeaSummary(adrId!),
                    ]);
                    setStages(latestAnalysis?.stages || latestAnalysis?.analysis?.stages || []);
                    setIdea(ideaSummaryData?.idea || '');
                    setSummary(ideaSummaryData?.summary || latestAnalysis?.message || '');
                }

                // Agent stats snapshot
                const statsEntries = await Promise.all(
                    (agentsData || []).map(async (a: any) => {
                        const id = a.id || a.name || a.role;
                        try {
                            const stats = await fetchAgentStats(id);
                            return [id, stats] as const;
                        } catch {
                            return [id, null] as const;
                        }
                    }),
                );
                setAgentStats(Object.fromEntries(statsEntries));

                // Gaps summary
                const gapsData = await fetchAgentGaps();
                setGaps({
                    critical: gapsData?.critical || [],
                    medium: gapsData?.medium || [],
                    enhancement: gapsData?.enhancement || [],
                });

            } catch (e: any) {
                setError(e.message || 'خطأ في جلب البيانات');
            } finally {
                setLoading(false);
            }
        }
        loadGeneralData();
    }, [adrId]);

    const handleDetails = async (agentName: string) => {
        setDetailsAgent(agentName);
        // Load detailed history for this agent (fallback to filtered events)
        try {
            const history = await fetchAgentHistory(agentName);
            const histEntries =
                history?.history?.map((h: any) => ({
                    time: h.timestamp || '',
                    description: h.summary || h.title || h.run_id || '',
                    confidence: h.confidence,
                    verdict: h.verdict,
                })) || [];
            setDetailsEvents(histEntries);
        } catch {
            setDetailsEvents(events.filter((ev) => ev.agent === agentName));
        }
    };

    const stats = useMemo(
        () => ({
            agentsCount: agents.length,
            eventsCount: events.length,
            stagesCount: stages.length,
        }), [agents, events, stages]);


    return (
        <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
            <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                    <p className="text-sm text-slate-500">تدفق الوكلاء · آخر تحليل مفعّل</p>
                    <h1 className="text-2xl font-bold text-slate-900">Agents Flow</h1>
                    <p className="text-slate-600">مؤشرات التحليل، الوكلاء، وسجل الأحداث المبنية على بيانات الباكند الحية.</p>
                </div>
                <StatusIndicators status={status || 'pending'} />
            </header>

            {loading && <div className="text-center text-gray-500">جاري التحميل...</div>}
            {error && <div className="text-center text-red-500">{error}</div>}

            {!loading && !error && (
                <>
                    <section className="grid gap-4 sm:grid-cols-3">
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                            <p className="text-xs text-slate-500">عدد الوكلاء</p>
                            <div className="text-2xl font-bold text-slate-900">{stats.agentsCount}</div>
                            <p className="text-xs text-slate-500 mt-1">/api/system/agents</p>
                        </div>
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                            <p className="text-xs text-slate-500">سجل الأحداث</p>
                            <div className="text-2xl font-bold text-slate-900">{stats.eventsCount}</div>
                            <p className="text-xs text-slate-500 mt-1">/api/events</p>
                        </div>
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                            <p className="text-xs text-slate-500">مراحل التحليل</p>
                            <div className="text-2xl font-bold text-slate-900">{stats.stagesCount}</div>
                            <p className="text-xs text-slate-500 mt-1">/api/analysis/latest</p>
                        </div>
                    </section>

                    {stages.length === 0 ? (
                        <div className="p-4 rounded-xl border border-dashed border-slate-300 text-center text-slate-500">
                            لا يوجد تحليل نشط حالياً. قم بإنشاء ADR أو تشغيل تحليل جديد.
                        </div>
                    ) : (
                        <WorkflowBoard stages={stages} />
                    )}

                    <section className="grid md:grid-cols-3 gap-4">
                        <div className="md:col-span-2">
                            <div className="flex gap-3 flex-wrap mb-4">
                                {agents.map(agent => (
                                    <AgentCard key={agent.id || agent.name} agent={agent} onDetails={() => handleDetails(agent.name)} />
                                ))}
                            </div>
                        </div>
                        <div className="md:col-span-1">
                            <IdeaSummary idea={idea} summary={summary || 'لا يوجد ملخص متاح'} />
                            <EventLog events={events} />
                        </div>
                    </section>

                    {/* لوحة أداء الوكلاء والزمن */}
                    <section className="grid md:grid-cols-2 gap-4">
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="font-bold text-slate-900">إحصاءات الوكلاء</h3>
                                <span className="text-xs text-slate-400">آخر تشغيلات</span>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="text-left text-slate-500">
                                            <th className="py-1">الوكيل</th>
                                            <th className="py-1">معدل الموافقة</th>
                                            <th className="py-1">الصرامة</th>
                                            <th className="py-1">عدد التشغيلات</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {agents.map((a) => {
                                            const stat = agentStats[a.id || a.name || a.role] || {};
                                            return (
                                                <tr key={a.id || a.name} className="border-t text-slate-700">
                                                    <td className="py-1">{a.name}</td>
                                                    <td className="py-1">{stat.approval_rate !== undefined ? `${Math.round(stat.approval_rate * 100)}%` : '—'}</td>
                                                    <td className="py-1">{stat.strictness !== undefined ? stat.strictness : '—'}</td>
                                                    <td className="py-1">{stat.total_runs ?? '—'}</td>
                                                </tr>
                                            );
                                        })}
                                        {!agents.length && (
                                            <tr><td colSpan={4} className="text-center text-slate-400 py-2">لا يوجد وكلاء</td></tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-2">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="font-bold text-slate-900">الفجوات والتغطية</h3>
                                <span className="text-xs text-slate-400">/api/agents/gaps</span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-xs">
                                <div>
                                    <div className="font-black text-rose-600 uppercase">حرج</div>
                                    {gaps.critical.map((g) => <div key={g.name} className="text-slate-700">• {g.name}</div>)}
                                    {!gaps.critical.length && <div className="text-slate-400">لا توجد فجوات حرجة</div>}
                                </div>
                                <div>
                                    <div className="font-black text-amber-600 uppercase">متوسط</div>
                                    {gaps.medium.map((g) => <div key={g.name} className="text-slate-700">• {g.name}</div>)}
                                    {!gaps.medium.length && <div className="text-slate-400">—</div>}
                                </div>
                                <div>
                                    <div className="font-black text-emerald-600 uppercase">تحسين</div>
                                    {gaps.enhancement.map((g) => <div key={g.name} className="text-slate-700">• {g.name}</div>)}
                                    {!gaps.enhancement.length && <div className="text-slate-400">—</div>}
                                </div>
                            </div>
                        </div>
                    </section>
                </>
            )}
            {detailsAgent && (
                <AgentDetailsModal agent={detailsAgent} events={detailsEvents} onClose={() => setDetailsAgent(null)} />
            )}
        </div>
    );
};

export default AgentsFlowPage;
