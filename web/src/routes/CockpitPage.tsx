import { useQuery } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import {
  Activity,
  Bot,
  FileText,
  Shield,
  TrendingUp,
  Zap
} from 'lucide-react';
import { useState } from 'react';
import {
  createDecision,
  fetchAgentsRegistry,
  fetchObservabilityStats,
  fetchSystemHealth,
  listDecisions,
  listProposals
} from '../api/queries';
import type {
  AgentRegistryEntry,
  AgentsRegistryResponse,
  Decision,
  ObservabilityStats,
  Proposal,
  SystemHealth
} from '../api/types';
import { CouncilPulse } from '../components/governance/CouncilPulse';
import { NewProposalModal } from '../components/governance/NewProposalModal';
import { SecretaryLogsWidget } from '../components/governance/SecretaryLogsWidget';

export default function CockpitPage() {
  const router = useRouter();
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

  const healthQuery = useQuery<SystemHealth>({
    queryKey: ['system-health'],
    queryFn: fetchSystemHealth,
    staleTime: 15_000,
  });

  const observabilityQuery = useQuery<ObservabilityStats>({
    queryKey: ['observability-stats'],
    queryFn: fetchObservabilityStats,
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
    <div className="space-y-8 pt-6 pb-20">
      {/* Sovereign Header & High-Level Pulse */}
      <section className="relative overflow-hidden rounded-[2.5rem] p-8 glass-panel sovereign-glow bg-gradient-to-br from-brand-primary/10 to-transparent">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-1">
            <h2 className="text-3xl font-black text-white flex items-center gap-3">
              <Shield className="w-8 h-8 text-brand-primary animate-pulse" />
              مجلس السيادة | Sovereign Council Hub
            </h2>
            <p className="text-slate-400 font-medium">Autonomous Governance & Consensus Command Center</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setProposalModalOpen(true)}
              className="px-6 py-3 rounded-2xl bg-brand-primary text-white font-black hover:scale-105 transition-transform sovereign-glow flex items-center gap-2"
            >
              <Zap className="w-4 h-4 text-brand-accent fill-brand-accent" />
              بذر فكرة جديدة
            </button>
          </div>
        </div>

        {/* Real-time Consultation Pulse visualization */}
        <CouncilPulse consultations={[
          { from: 'architect', to: 'steward', type: 'inquiry' },
          { from: 'refactoring', to: 'testing', type: 'safety_check' }
        ]} />
      </section>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Column: Proposals & Secretary Logs (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Executive Briefing Section */}
          <section className="glass-panel rounded-3xl p-6 bg-slate-900/40 relative overflow-hidden group">
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-primary/10 rounded-full blur-3xl" />
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-xl text-white flex items-center gap-3">
                <span className="p-2 bg-indigo-500/20 rounded-xl text-indigo-400">🏛️</span>
                Executive Briefing
              </h3>
              <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
                <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                <span className="text-[10px] font-black tracking-widest text-slate-300">LIVE FEED</span>
              </div>
            </div>
            <SecretaryLogsWidget />
          </section>

          {/* Proposals Section */}
          <section className="glass-panel rounded-3xl p-6 space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-xl text-white flex items-center gap-3">
                <span className="p-2 bg-brand-soft/20 rounded-xl text-brand-base">
                  <FileText className="w-6 h-6" />
                </span>
                مراجعة المقترحات السيادية
              </h3>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              {(proposalsQuery.data?.proposals || []).slice(0, 4).map((p) => (
                <div
                  key={p.id}
                  className="p-5 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 hover:border-brand-primary/30 transition-all group"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="p-2 bg-slate-800 rounded-lg group-hover:text-brand-base transition-colors">
                      <Zap className="w-4 h-4" />
                    </div>
                    <span className="text-[9px] font-black px-2 py-1 rounded bg-brand-primary/20 text-brand-primary">
                      {p.state.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-base font-bold text-white mb-2">{p.title}</p>
                  <p className="text-xs text-slate-400 mb-6 line-clamp-2">
                    {p.reason || 'تحليل جاري بواسطة مجلس السيادة...'}
                  </p>
                  <div className="flex gap-3 mt-auto">
                    <button
                      onClick={() => handleDecision(p.id, 'approved')}
                      className="flex-1 py-2 rounded-xl bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/20 hover:bg-emerald-500 hover:text-white transition-all text-xs"
                    >
                      موافقة
                    </button>
                    <button
                      onClick={() => handleDecision(p.id, 'rejected')}
                      className="flex-1 py-2 rounded-xl bg-rose-500/20 text-rose-400 font-bold border border-rose-500/20 hover:bg-rose-500 hover:text-white transition-all text-xs"
                    >
                      رفض
                    </button>
                  </div>
                </div>
              ))}
              {(!proposalsQuery.data?.proposals || proposalsQuery.data.proposals.length === 0) && (
                <div className="col-span-2 text-center py-16 text-slate-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-5" />
                  <p className="font-medium">بانتظار بذر أفكار جديدة في المجلس</p>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Right Column: Agents & Health (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Sovereign Metrics Cluster */}
          <section className="glass-panel rounded-3xl p-6 space-y-6">
            <h3 className="font-bold text-white flex items-center gap-3 mb-2">
              <Activity className="w-5 h-5 text-brand-secondary" />
              Sovereign Metrics
            </h3>
            <div className="space-y-4">
              <MetricItem
                label="صحة النظام"
                value={healthQuery.data?.status || 'OPTIMAL'}
                subtext={`Active Agents: ${healthQuery.data?.active_agents || '-'}`}
                color="text-emerald-400"
              />
              <MetricItem
                label="النمو السيادي"
                value="PHASE 7"
                subtext="Aesthetic Sovereignty"
                icon={<TrendingUp className="w-4 h-4" />}
                color="text-indigo-400"
              />
              <MetricItem
                label="نشاط التشاور"
                value={observabilityQuery.data ? `${observabilityQuery.data.total_events} OPS` : '...'}
                subtext={observabilityQuery.data?.latest_event?.message || 'Peer-to-Peer Events'}
                color="text-brand-base"
              />
              <MetricItem
                label="معيار الغاية"
                value={observabilityQuery.data?.average_purpose_score ? `${observabilityQuery.data.average_purpose_score}/100` : '-'}
                subtext="Sovereign Purpose Score"
                icon={<Shield className="w-4 h-4" />}
                color="text-emerald-400"
              />
              <MetricItem
                label="ميزانية الدورة"
                value={observabilityQuery.data?.cycle_token_usage ? `${(observabilityQuery.data.cycle_token_usage / 1000).toFixed(1)}k` : '-'}
                subtext={`Limit: ${(observabilityQuery.data?.budget_limit || 50000) / 1000}k Tokens`}
                icon={<Zap className="w-4 h-4" />}
                color={
                  (observabilityQuery.data?.cycle_token_usage || 0) > (observabilityQuery.data?.budget_limit || 50000) * 0.8
                    ? "text-rose-400"
                    : "text-sky-400"
                }
              />
            </div>
          </section>

          {/* Agents Column List */}
          <section className="glass-panel rounded-3xl p-6 space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-white flex items-center gap-3">
                <Bot className="w-5 h-5 text-brand-primary" />
                أعضاء المجلس
              </h3>
              <span className="text-[10px] font-black text-slate-500">{agents.length} ACTIVE</span>
            </div>
            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
              {agents.map((agent: AgentRegistryEntry) => (
                <div
                  key={agent.id}
                  onClick={() => router.navigate({ to: '/agent/$agentId', params: { agentId: agent.id } })}
                  className="flex items-center gap-4 p-3 rounded-2xl bg-white/5 border border-white/10 hover:border-brand-primary/30 hover:bg-white/10 transition-all cursor-pointer group"
                >
                  <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-500 group-hover:text-brand-base transition-colors">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-white truncate">{agent.name}</p>
                    <p className="text-[10px] text-slate-500 font-bold uppercase">{agent.department}</p>
                  </div>
                  <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

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

function MetricItem({ label, value, subtext, icon, color = "text-white" }: { label: string; value: string | number; subtext?: string; icon?: React.ReactNode; color?: string }) {
  return (
    <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
      <div className="flex justify-between items-start">
        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{label}</span>
        {icon && <span className={color}>{icon}</span>}
      </div>
      <p className={`text-xl font-black mt-1 ${color}`}>{value}</p>
      {subtext && <p className="text-[10px] text-slate-500 font-bold mt-0.5">{subtext}</p>}
    </div>
  );
}
