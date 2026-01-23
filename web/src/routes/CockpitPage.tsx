import { useQuery } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import {
  Activity,
  Bot,
  CheckCircle2,
  Clock,
  FileText
} from 'lucide-react';
import { useState } from 'react';
import {
  createDecision,
  fetchAgentsRegistry,
  fetchObservabilityStats,
  fetchSystemHealth,
  listConflicts,
  listDecisions,
  listGovernanceTimeline,
  listProposals
} from '../api/queries';
import type {
  AgentRegistryEntry,
  AgentsRegistryResponse,
  Conflict,
  Decision,
  GovernanceEvent,
  Proposal
} from '../api/types';
import { NewProposalModal } from '../components/governance/NewProposalModal';
import { SecretaryLogsWidget } from '../components/governance/SecretaryLogsWidget';
import { useSCPStream } from '../hooks/useSCPStream';
import useCockpitStore from '../state/cockpitStore';

export default function CockpitPage() {
  const router = useRouter();
  const { activeAgentId } = useCockpitStore();
  const { timeline } = useSCPStream();
  const [isProposalModalOpen, setProposalModalOpen] = useState(false);

  const proposalsQuery = useQuery<{ proposals: Proposal[] }>({
    queryKey: ['proposals'],
    queryFn: () => listProposals(),
    staleTime: 5_000,
  });

  const decisionsQuery = useQuery<{ decisions: Decision[] }>({
    queryKey: ['decisions'],
    queryFn: () => listDecisions(),
    staleTime: 5_000,
  });

  const agentsQuery = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
    retry: 1,
  });

  const healthQuery = useQuery({
    queryKey: ['system-health'],
    queryFn: fetchSystemHealth,
    staleTime: 15_000,
  });

  const observabilityQuery = useQuery({
    queryKey: ['observability-stats'],
    queryFn: fetchObservabilityStats,
    staleTime: 15_000,
  });

  const conflictsQuery = useQuery<{ conflicts: Conflict[] }>({
    queryKey: ['governance-conflicts'],
    queryFn: () => listConflicts(),
    staleTime: 15_000,
  });

  const timelineQuery = useQuery<{ timeline: GovernanceEvent[] }>({
    queryKey: ['governance-timeline'],
    queryFn: () => listGovernanceTimeline(),
    staleTime: 15_000,
  });

  const agents = agentsQuery.data?.agents ?? [];

  const handleDecision = (proposalId: string, decision: 'approved' | 'rejected' | 'deferred') => {
    createDecision({
      proposal_id: proposalId,
      decision,
      rationale: `Decision recorded via cockpit overview (${decision})`,
      signed_by: 'operator',
    })
      .then(() => {
        proposalsQuery.refetch();
        decisionsQuery.refetch();
      })
      .catch((err) => console.error('Decision error:', err));
  };

  return (
    <div className="space-y-6 pt-4">
      <section className="grid lg:grid-cols-2 gap-6">
        {/* Proposal Overview */}
        <div className="glass rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-ink flex items-center gap-2">
              <FileText className="w-5 h-5 text-brand-base" />
              الأفكار قيد المراجعة
            </h3>
            <button
              className="px-3 py-1.5 rounded-xl bg-brand-soft text-brand-base text-xs font-bold hover:bg-brand-base hover:text-white transition-colors"
              onClick={() => setProposalModalOpen(true)}
            >
              بذر فكرة +
            </button>
          </div>
          <div className="space-y-3">
            {(proposalsQuery.data?.proposals || []).slice(0, 4).map((p) => (
              <div
                key={p.id}
                className="p-4 rounded-2xl border border-slate-100 bg-white/70 flex items-center justify-between group hover:border-brand-base/20 transition-all"
              >
                <div>
                  <p className="text-sm font-bold text-ink">{p.title}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {p.state} · {(p.reason || '').slice(0, 50)}...
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDecision(p.id, 'approved')}
                    className="p-2 rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-colors"
                    title="موافقة"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDecision(p.id, 'rejected')}
                    className="p-2 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-600 hover:text-white transition-colors"
                    title="رفض"
                  >
                    <Activity className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {(!proposalsQuery.data?.proposals || proposalsQuery.data.proposals.length === 0) && (
              <div className="text-center py-10 text-slate-400">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-10" />
                <p className="text-sm">لا توجد مقترحات تتطلب اتخاذ قرار حالياً</p>
              </div>
            )}
          </div>
        </div>

        {/* Live Timeline Snapshot */}
        <div className="glass rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-ink flex items-center gap-2">
              <Activity className="w-5 h-5 text-brand-base" />
              أحدث التنبيهات والأحداث
            </h3>
            <button
              className="text-xs text-brand-base font-bold hover:underline"
              onClick={() => router.navigate({ to: '/timeline' })}
            >
              عرض السجل الكامل →
            </button>
          </div>
          <div className="space-y-2">
            {(timeline || []).slice(0, 6).map((event, idx) => (
              <div
                key={event.id || idx}
                className="flex items-center gap-3 p-3 rounded-xl border border-slate-50 bg-white/50"
              >
                <div className={`w-1.5 h-1.5 rounded-full ${event.severity === 'critical' ? 'bg-rose-500 animate-pulse' : 'bg-brand-base'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold text-ink truncate">{event.label}</p>
                  <p className="text-[10px] text-slate-400">
                    {new Date(event.time).toLocaleTimeString()} · Source: {event.source || 'SYSTEM'}
                  </p>
                </div>
                <span
                  className={`text-[9px] px-2 py-0.5 rounded-full font-bold border ${event.severity === 'critical'
                    ? 'bg-rose-50 text-rose-700 border-rose-100'
                    : event.severity === 'warn'
                      ? 'bg-amber-50 text-amber-700 border-amber-100'
                      : 'bg-slate-100 text-slate-600 border-slate-200'
                    }`}
                >
                  {event.severity?.toUpperCase() || 'INFO'}
                </span>
              </div>
            ))}
            {(!timeline || timeline.length === 0) && (
              <div className="text-center py-10 text-slate-400">
                <Clock className="w-8 h-8 mx-auto mb-2 opacity-10" />
                <p className="text-sm">بانتظار الأحداث المباشرة...</p>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-4">
        <div className="glass rounded-3xl p-4 space-y-2">
          <h4 className="font-semibold text-ink">صحة النظام</h4>
          <p className="text-sm text-slate-500">
            {(healthQuery.data as any)?.status || '...'} · {(healthQuery.data as any)?.api || ''}
          </p>
          <p className="text-xs text-slate-500">Agents: {(healthQuery.data as any)?.active_agents ?? '-'}</p>
        </div>
        <div className="glass rounded-3xl p-4 space-y-2">
          <h4 className="font-semibold text-ink">المراقبة</h4>
          <p className="text-sm text-slate-500">أحداث: {(observabilityQuery.data as any)?.total_events ?? '-'}</p>
          <p className="text-xs text-slate-500">أحدث: {(observabilityQuery.data as any)?.latest_event?.message ?? '—'}</p>
        </div>
        <div className="glass rounded-3xl p-4 space-y-2">
          <h4 className="font-semibold text-ink">التعارضات</h4>
          <p className="text-sm text-slate-500">عدد التعارضات: {conflictsQuery.data?.conflicts?.length ?? 0}</p>
          {conflictsQuery.data?.conflicts?.slice(0, 2).map((c) => (
            <p key={c.id} className="text-xs text-slate-500 truncate">
              • {c.title || c.id}
            </p>
          ))}
        </div>
        <div className="glass rounded-3xl p-4 space-y-2">
          <h4 className="font-semibold text-ink">الزمن الحوكمي</h4>
          <p className="text-sm text-slate-500">آخر أحداث: {timelineQuery.data?.timeline?.length ?? 0}</p>
          {timelineQuery.data?.timeline?.slice(0, 2).map((t) => (
            <p key={t.id} className="text-xs text-slate-500 truncate">
              • {t.label || t.type} — {new Date(t.timestamp || '').toLocaleTimeString()}
            </p>
          ))}
        </div>
      </section>

      {/* Cycle 16: Executive Briefing (Secretary Logs) */}
      <section className="glass rounded-3xl p-6 bg-gradient-to-r from-slate-900 to-slate-800 text-white relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 opacity-50"></div>
        <div className="flex items-center justify-between mb-4 relative z-10">
          <h3 className="font-bold text-lg flex items-center gap-3">
            <span className="text-2xl">🏛️</span>
            Executive Briefing (ملخص السكرتارية التنفيذي)
          </h3>
          <span className="text-[10px] uppercase tracking-widest bg-white/10 px-3 py-1 rounded-full">CONFIDENTIAL</span>
        </div>
        <SecretaryLogsWidget />
      </section>

      {/* Agents Registry Grid */}
      <section className="glass rounded-3xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-ink flex items-center gap-2">
            <Bot className="w-5 h-5 text-brand-base" />
            فريق الوكلاء النشط (Active Agents)
          </h3>
          <button
            className="text-xs text-brand-base font-bold hover:underline"
            onClick={() => router.navigate({ to: '/agents-flow' })}
          >
            عرض تدفق العمل الكامل ←
          </button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {agents.map((agent: AgentRegistryEntry) => (
            <div
              key={agent.id}
              onClick={() => router.navigate({ to: '/agent/$agentId', params: { agentId: agent.id } })}
              className="p-4 rounded-2xl border border-slate-100 bg-white hover:border-brand-base/30 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 group-hover:text-brand-base transition-colors">
                  <Bot className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-black text-ink">{agent.name}</p>
                  <p className="text-[10px] text-slate-400 font-bold uppercase">{agent.department}</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold border ${agent.status === 'active' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-slate-50 text-slate-500 border-slate-100'}`}>
                  {agent.status.toUpperCase()}
                </span>
                <span className="text-[9px] text-slate-400">Fidelity: {agent.fidelity}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Decision Summary Metrics */}
      <section className="grid sm:grid-cols-4 gap-4">
        <SummaryCard title="Current Agent" value={activeAgentId} icon={<Bot className="w-4 h-4" />} />
        <SummaryCard title="Decisions Recorded" value={decisionsQuery.data?.decisions?.length || 0} icon={<CheckCircle2 className="w-4 h-4" />} />
        <SummaryCard title="Pending Proposals" value={proposalsQuery.data?.proposals?.filter(p => p.state !== 'decision').length || 0} icon={<FileText className="w-4 h-4" />} />
        <SummaryCard title="System Health" value="OPTIMAL" color="text-emerald-600" icon={<Activity className="w-4 h-4" />} />
      </section>

      {isProposalModalOpen && (
        <NewProposalModal
          isOpen={isProposalModalOpen}
          onClose={() => {
            setProposalModalOpen(false);
            proposalsQuery.refetch();
          }}
        />
      )}
    </div>
  );
}

function SummaryCard({ title, value, icon, color = "text-ink" }: { title: string; value: string | number; icon: React.ReactNode; color?: string }) {
  return (
    <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center gap-4">
      <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
        {icon}
      </div>
      <div>
        <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">{title}</p>
        <p className={`text-lg font-bold ${color}`}>{value}</p>
      </div>
    </div>
  );
}
