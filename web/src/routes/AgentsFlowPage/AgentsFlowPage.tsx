import { useEffect, useMemo, useState } from 'react';
import type { AgentInfo } from './AgentCard';
import AgentCard from './AgentCard';
import AgentDetailsModal from './AgentDetailsModal';
import { fetchAgents, fetchEvents, fetchIdeaSummary, fetchLatestAnalysis, fetchStatus } from './api';
import type { EventInfo } from './EventLog';
import EventLog from './EventLog';
import IdeaSummary from './IdeaSummary';
import StatusIndicators from './StatusIndicators';
import WorkflowBoard from './WorkflowBoard';

// Placeholder ADR id: يتطلب ربط حقيقي بـ /api/analysis/latest أو اختيار ADR من الواجهة.
const adrId = 'latest';

const AgentsFlowPage = () => {
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

    useEffect(() => {
        async function loadData() {
            setLoading(true);
            setError('');
            try {
                const [agentsData, latestAnalysis, eventsData, statusData, ideaSummaryData] = await Promise.all([
                    fetchAgents(),
                    fetchLatestAnalysis(),
                    fetchEvents(),
                    fetchStatus(),
                    fetchIdeaSummary(adrId), // يبقى موك/placeholder حتى يُربط بمعرّف ADR حقيقي
                ]);
                setAgents(agentsData.map((a: any) => ({
                    id: a.id || a.name,
                    name: a.name,
                    role: a.role,
                    status: a.status,
                    lastTask: a.lastTask || '',
                    recommendation: a.recommendation || '',
                })));
                // latestAnalysis قد يرجع حالة "empty" أو "pending" أو نتائج تحليل كاملة.
                const resolvedStages = latestAnalysis?.stages || latestAnalysis?.analysis?.stages || [];
                setStages(resolvedStages);
                const normalizedEvents = Array.isArray(eventsData?.events)
                    ? eventsData.events.map((e: any) => ({
                        time: e.timestamp || '',
                        agent: e.user_id || e.trace_id || 'system',
                        description: e.message || e.payload?.message || e.type || '',
                        type: (e.type || e.event_type || 'info').toLowerCase(),
                    }))
                    : Array.isArray(eventsData)
                        ? eventsData
                        : [];
                setEvents(normalizedEvents);
                setStatus(statusData.status || latestAnalysis?.status || '');
                setIdea(ideaSummaryData?.idea || '');
                setSummary(ideaSummaryData?.summary || latestAnalysis?.message || '');
            } catch (e: any) {
                setError(e.message || 'خطأ في جلب البيانات');
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    const handleDetails = (agentName: string) => {
        setDetailsAgent(agentName);
        setDetailsEvents(events.filter(ev => ev.agent === agentName));
    };

    const stats = useMemo(() => ({
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
                </>
            )}
            {detailsAgent && (
                <AgentDetailsModal agent={detailsAgent} events={detailsEvents} onClose={() => setDetailsAgent(null)} />
            )}
        </div>
    );
};

export default AgentsFlowPage;
