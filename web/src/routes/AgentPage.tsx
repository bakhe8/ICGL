import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useRouter } from '@tanstack/react-router';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { fetchAgentsRegistry, listProposals, listDecisions, listConflicts, runAgent } from '../api/queries';
import type { AgentsRegistryResponse, Proposal, Decision, Conflict, AgentRunResult } from '../api/types';
import { fallbackAgents } from '../data/fallbacks';
import { useSCPStream } from '../hooks/useSCPStream';
import { AgentChat } from '../components/agent/AgentChat';
import { AgentHistory } from '../components/agent/AgentHistory';

function buildAgentEvents(
  agentId: string,
  proposals: Proposal[],
  decisions: Decision[],
  conflicts: Conflict[],
) {
  interface AgentEvent { id: string; type: 'proposal' | 'decision' | 'conflict'; title: string; subtitle: string; timestamp: string; targetId?: string; }
  const events: AgentEvent[] = [];
  (proposals || [])
    .filter((p) => p.author === agentId)
    .forEach((p) => {
      events.push({
        id: p.id,
        type: 'proposal',
        title: p.title,
        subtitle: p.state,
        timestamp: p.created_at || 'Recently',
        targetId: p.id,
      });
    });
  (decisions || [])
    .filter((d) => d.rationale?.includes(agentId)) // loose coupling check
    .forEach((d) => {
      events.push({
        id: d.id,
        type: 'decision',
        title: `Decision: ${d.decision}`,
        subtitle: d.rationale || '',
        timestamp: d.timestamp || 'Recently',
        targetId: d.proposal_id,
      });
    });
  (conflicts || [])
    .filter((c) => c.involved_agents.includes(agentId))
    .forEach((c) => {
      events.push({
        id: c.id,
        type: 'conflict',
        title: c.title,
        subtitle: c.state,
        timestamp: c.created_at || 'Recently',
        targetId: c.id,
      });
    });
  return events.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
}

export default function AgentPage() {
  const router = useRouter();
  const { agentId } = useParams({ from: '/agent/$agentId' });
  const { connection } = useSCPStream();

  const { data } = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    initialData: { agents: fallbackAgents },
  });

  const proposalsQuery = useQuery({ queryKey: ['proposals'], queryFn: () => listProposals() });
  const decisionsQuery = useQuery({ queryKey: ['decisions'], queryFn: () => listDecisions() });
  const conflictsQuery = useQuery({ queryKey: ['conflicts'], queryFn: () => listConflicts() });

  const agent = data?.agents.find((a) => a.id === agentId);

  const uniqueProposals =
    proposalsQuery.data?.proposals && proposalsQuery.data.proposals.length
      ? Array.from(new Map(proposalsQuery.data.proposals.map((p) => [p.id, p])).values())
      : [];

  const runMutation = useMutation<AgentRunResult, Error>({
    mutationKey: ['run-agent', agentId],
    mutationFn: () =>
      runAgent(agent?.role || agent?.id || 'unknown', {
        title: `Run ${agent?.name || 'Unknown'}`,
        context: `Manual run from Console`,
      }),
  });

  if (!agent) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <h2 className="text-xl font-bold text-slate-700">Agent Not Found</h2>
        <p className="text-slate-500">The agent "{agentId}" could not be found in the registry.</p>
        <button
          className="text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1"
          onClick={() => router.navigate({ to: '/' })}
        >
          <ArrowRight className="w-4 h-4" />
          Back to Cockpit
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-w-7xl mx-auto pb-10">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm">
        <button
          className="flex items-center gap-1 text-indigo-600 hover:text-indigo-700 font-semibold"
          onClick={() => router.navigate({ to: '/' })}
        >
          <ArrowRight className="w-4 h-4" />
          رجوع
        </button>
        <span className="text-slate-400">/</span>
        <span className="text-slate-600 font-medium">{agent.department}</span>
      </div>

      <section className="glass rounded-3xl p-6 space-y-4 border border-slate-200/50 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-emerald-400 to-indigo-500 opacity-20"></div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between relative z-10">
          <div>
            <p className="text-xs text-indigo-500 font-bold tracking-wider uppercase mb-1">{agent.department}</p>
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">{agent.name}</h2>
            <p className="text-sm text-slate-500 mt-1 max-w-2xl">{agent.description}</p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-semibold">
            <span className={`px-3 py-1 rounded-full border ${agent.status === 'active' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
              {agent.status === 'active' ? '● Active' : '○ Idle'}
            </span>
            <span className="px-3 py-1 rounded-full bg-slate-50 text-slate-700 border border-slate-200">
              Fidelity: {agent.fidelity}
            </span>
            <span className={`px-3 py-1 rounded-full border ${connection === 'open' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
              {connection === 'open' ? '⚡ Connected' : '⚠ Disconnected'}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-3 pt-2">
          <button
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium flex items-center gap-2 shadow-sm transition-all active:scale-95"
            onClick={() => runMutation.mutate()}
            disabled={runMutation.isPending}
          >
            <CheckCircle2 className="w-4 h-4" />
            {runMutation.isPending ? 'جاري التشغيل...' : 'تشغيل الوكيل (Run Agent)'}
          </button>
          <span className="px-3 py-2 rounded-xl bg-slate-50 text-slate-500 text-xs border border-slate-200 font-mono">
            ID: {agent.id}
          </span>
        </div>

        {/* Agent Run Result Area */}
        {runMutation.data && (
          <div className="mt-4 p-4 rounded-xl bg-emerald-50/50 border border-emerald-100 text-sm">
            <h4 className="font-bold text-emerald-900 mb-2 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Analysis Result
            </h4>
            <div className="whitespace-pre-wrap text-slate-800 leading-relaxed font-sans">{runMutation.data.analysis}</div>
          </div>
        )}
      </section>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column: Capabilities & Signals */}
        <div className="space-y-4">
          <div className="glass rounded-2xl p-5 border border-slate-200/60">
            <h3 className="font-bold text-slate-800 mb-3 text-sm">القدرات (Capabilities)</h3>
            <div className="space-y-2">
              {agent.capabilities.map((cap) => (
                <div key={cap} className="flex items-center gap-2 text-xs p-2 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                  <span className="text-slate-700 font-medium">{cap}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="glass rounded-2xl p-5 border border-slate-200/60">
            <h3 className="font-bold text-slate-800 mb-3 text-sm">الإشارات (Signals)</h3>
            <div className="flex flex-wrap gap-2 text-[10px]">
              {(agent.signals || ['No live signals']).map((signal) => (
                <span key={signal} className="px-2 py-1 rounded-md bg-slate-100 text-slate-600 font-mono border border-slate-200">
                  {signal}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Middle Column: Chat & Interaction */}
        <div className="lg:col-span-2 space-y-6">
          <AgentChat agentId={agentId} />

          <section className="glass rounded-2xl p-5 border border-slate-200/60">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800">سجل الأحداث (Timeline)</h3>
              <span className="text-xs px-2 py-1 rounded bg-slate-100 text-slate-500">Live Feed</span>
            </div>
            <AgentHistory
              events={buildAgentEvents(
                agent.id,
                uniqueProposals,
                decisionsQuery.data?.decisions || [],
                conflictsQuery.data?.conflicts || []
              )}
            />
          </section>
        </div>
      </div>
    </div>
  );
}
