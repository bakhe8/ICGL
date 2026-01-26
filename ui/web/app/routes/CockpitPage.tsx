import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  Bot,
  FileText,
  Shield,
  TrendingUp,
  Zap
} from 'lucide-react';
import { useState } from 'react';
import { fetchJson } from '../api/client';
import {
  createDecision,
  fetchAgentsRegistry,
  fetchObservabilityStats,
  fetchSystemHealth,
  listDecisions,
  listProposals
} from '../api/queries';
import type {
  AgentsRegistryResponse,
  Decision,
  ObservabilityStats,
  Proposal,
  SystemHealth
} from '../api/types';
import { ExecutiveConsole } from '../components/executive/ExecutiveConsole';
import { CouncilGrid } from '../components/governance/CouncilGrid';
import { CouncilPulse } from '../components/governance/CouncilPulse';
import { NewProposalModal } from '../components/governance/NewProposalModal';
import { SecretaryLogsWidget } from '../components/governance/SecretaryLogsWidget';

export default function CockpitPage() {
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

  const trafficQuery = useQuery({
    queryKey: ['system-traffic'],
    queryFn: () => fetchJson<{ traffic: { from: string, to: string, type: string }[] }>('/api/system/traffic'),
    refetchInterval: 2000
  });

  const activeTraffic = trafficQuery.data?.traffic || [];

  const observabilityQuery = useQuery<ObservabilityStats>({
    queryKey: ['observability-stats'],
    queryFn: fetchObservabilityStats,
    staleTime: 15_000,
  });

  const agents = agentsQuery.data?.agents ?? [];


  const [toast, setToast] = useState<{ message: string; type: 'success' | 'info' } | null>(null);

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
        const actionText = decision === 'approved' ? 'Policy Enacted' : 'Decision Recorded';
        setToast({
          message: `✅ ${actionText}! The System will now align with this mandate.`,
          type: 'success'
        });
        setTimeout(() => setToast(null), 5000);
      })
      .catch((err) => {
        console.error('Decision error:', err);
        setToast({ message: '❌ Signing Failed. Check logs.', type: 'info' });
      });
  };

  return (
    <div className="space-y-8 pt-6 pb-20 relative">
      {toast && (
        <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-4">
          <div className="bg-slate-900/90 text-white px-6 py-3 rounded-full shadow-2xl backdrop-blur-md flex items-center gap-3 border border-indigo-500/50">
            <Shield className="w-5 h-5 text-emerald-400" />
            <span className="font-bold text-sm tracking-wide">{toast.message}</span>
          </div>
        </div>
      )}
      {/* Sovereign Header & High-Level Pulse */}
      <section className="relative overflow-hidden rounded-[2.5rem] p-8 glass-panel sovereign-glow bg-gradient-to-br from-brand-primary/10 to-transparent">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-1">
            <h2 className="text-3xl font-black text-slate-900 flex items-center gap-3">
              <Shield className="w-8 h-8 text-brand-primary animate-pulse" />
              مجلس السيادة | Sovereign Council Hub
            </h2>
            <p className="text-slate-500 font-medium">Autonomous Governance & Consensus Command Center</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setProposalModalOpen(true)}
              className="px-6 py-3 rounded-2xl bg-brand-primary text-slate-900 font-black hover:scale-105 transition-transform sovereign-glow flex items-center gap-2"
            >
              <Zap className="w-4 h-4 text-brand-accent fill-brand-accent" />
              بذر فكرة جديدة
            </button>
          </div>
        </div>

        {/* Real-time Consultation Pulse visualization */}
        {/* Uses real traffic data from backend /api/system/traffic */}
        <CouncilPulse consultations={activeTraffic.length > 0 ? activeTraffic : [
          { from: 'system', to: 'idle', type: 'pulse' }
        ]} />
      </section>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Column: Proposals & Secretary Logs (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Executive Briefing Section */}
          <section className="space-y-6">
            <ExecutiveConsole />

            <section className="glass-panel rounded-3xl p-6 bg-white/60 relative overflow-hidden group">
              {/* ... Secretary Header ... */}
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-primary/10 rounded-full blur-3xl" />
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-xl text-slate-900 flex items-center gap-3">
                  <span className="p-2 bg-indigo-500/20 rounded-xl text-indigo-400">🏛️</span>
                  Executive Briefing
                </h3>
                <div className="flex items-center gap-2 px-3 py-1 bg-slate-50 rounded-full border border-slate-200">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                  <span className="text-[10px] font-black tracking-widest text-slate-600">LIVE FEED</span>
                </div>
              </div>
              <SecretaryLogsWidget />
            </section>
          </section>

          {/* Proposals Section */}
          <section className="glass-panel rounded-3xl p-6 space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-xl text-slate-900 flex items-center gap-3">
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
                  className="p-5 rounded-2xl border border-slate-200 bg-slate-50 hover:bg-white/10 hover:border-brand-primary/30 transition-all group"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="p-2 bg-slate-100/50 rounded-lg group-hover:text-brand-base transition-colors">
                      <Zap className="w-4 h-4" />
                    </div>
                    <span className="text-[9px] font-black px-2 py-1 rounded bg-brand-primary/20 text-brand-primary">
                      {(p.state || 'pending').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-base font-bold text-slate-900 mb-2">{p.title}</p>
                  <p className="text-xs text-slate-500 mb-6 line-clamp-2">
                    {p.reason || 'تحليل جاري بواسطة مجلس السيادة...'}
                  </p>
                  {p.predicted_benefit && (
                    <div className="mb-4 bg-emerald-50 rounded-lg p-3 text-[10px] text-emerald-700 font-medium flex gap-2 items-start border border-emerald-100">
                      <span className="font-bold shrink-0">✨ المنفعة المتوقعة:</span>
                      <span className="line-clamp-3 leading-relaxed">{p.predicted_benefit}</span>
                    </div>
                  )}
                  <div className="flex gap-3 mt-auto">
                    <button
                      onClick={() => handleDecision(p.id, 'approved')}
                      className="flex-1 py-2 rounded-xl bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/20 hover:bg-emerald-500 hover:text-slate-900 transition-all text-xs"
                    >
                      موافقة
                    </button>
                    <button
                      onClick={() => handleDecision(p.id, 'rejected')}
                      className="flex-1 py-2 rounded-xl bg-rose-500/20 text-rose-400 font-bold border border-rose-500/20 hover:bg-rose-500 hover:text-slate-900 transition-all text-xs"
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
            <h3 className="font-bold text-slate-900 flex items-center gap-3 mb-2">
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

        </div>

        {/* Council Grid Section (Full Width) */}
        <section className="glass-panel rounded-[2.5rem] p-8 space-y-8 w-full lg:col-span-12">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h3 className="text-2xl font-black text-slate-900 flex items-center gap-4">
              <Bot className="w-8 h-8 text-brand-primary shrink-0" />
              <span className="truncate">سجل الوكلاء السيادي | Council Registry</span>
            </h3>

            <div className="flex items-center gap-3 shrink-0">
              <span className="px-4 py-1.5 rounded-full bg-brand-primary/10 text-brand-primary text-[10px] font-black tracking-widest border border-brand-primary/20 whitespace-nowrap">
                {agents.length} ACTIVE NODES
              </span>
            </div>
          </div>

          <CouncilGrid agents={agents} />
        </section >
      </div >

      {isProposalModalOpen && (
        <NewProposalModal
          isOpen={isProposalModalOpen}
          onClose={() => {
            setProposalModalOpen(false);
            proposalsQuery.refetch();
          }}
        />
      )
      }
    </div >
  );
}

function MetricItem({ label, value, subtext, icon, color = "text-slate-900" }: { label: string; value: string | number; subtext?: string; icon?: React.ReactNode; color?: string }) {
  return (
    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
      <div className="flex justify-between items-start">
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{label}</span>
        {icon && <span className={color}>{icon}</span>}
      </div>
      <p className={`text-xl font-black mt-1 ${color}`}>{value}</p>
      {subtext && <p className="text-[10px] text-slate-500 font-bold mt-0.5">{subtext}</p>}
    </div>
  );
}
