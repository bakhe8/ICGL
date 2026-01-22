import { useEffect, useState } from 'react';
import type { AgentInfo } from './AgentCard';
import AgentCard from './AgentCard';
import AgentDetailsModal from './AgentDetailsModal';
import { fetchAgents, fetchAnalysis, fetchEvents, fetchIdeaSummary, fetchStatus } from './api';
import type { EventInfo } from './EventLog';
import EventLog from './EventLog';
import HeaderBar from './HeaderBar';
import IdeaSummary from './IdeaSummary';
import StatusIndicators from './StatusIndicators';
import WorkflowBoard from './WorkflowBoard';

const adrId = 'latest'; // يمكن استبداله بـ adrId حقيقي عند التنفيذ الفعلي

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
                const [agentsData, analysisData, eventsData, statusData, ideaSummaryData] = await Promise.all([
                    fetchAgents(),
                    fetchAnalysis(adrId),
                    fetchEvents(),
                    fetchStatus(),
                    fetchIdeaSummary(adrId),
                ]);
                setAgents(agentsData.map((a: any) => ({
                    name: a.name,
                    role: a.role,
                    status: a.status,
                    lastTask: a.lastTask || '',
                    recommendation: a.recommendation || '',
                })));
                setStages(analysisData.stages || []);
                setEvents(eventsData || []);
                setStatus(statusData.status || '');
                setIdea(ideaSummaryData.idea || '');
                setSummary(ideaSummaryData.summary || '');
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

    return (
        <div className="min-h-screen bg-gray-50">
            <HeaderBar />
            <div className="max-w-6xl mx-auto p-6">
                {loading && <div className="text-center text-gray-500">جاري التحميل...</div>}
                {error && <div className="text-center text-red-500">{error}</div>}
                {!loading && !error && (
                    <>
                        <WorkflowBoard stages={stages} />
                        <StatusIndicators status={status} />
                        <div className="flex gap-4 flex-wrap mb-6">
                            {agents.map(agent => (
                                <AgentCard key={agent.name} agent={agent} onDetails={() => handleDetails(agent.name)} />
                            ))}
                        </div>
                        <EventLog events={events} />
                        <IdeaSummary idea={idea} summary={summary} />
                    </>
                )}
            </div>
            {detailsAgent && (
                <AgentDetailsModal agent={detailsAgent} events={detailsEvents} onClose={() => setDetailsAgent(null)} />
            )}
        </div>
    );
};

export default AgentsFlowPage;
