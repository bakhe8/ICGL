import { useQuery } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import {
  Activity,
  Bot,
  CheckCircle2,
  Clock,
  FileText,
  Globe2,
  Shield,
  Workflow
} from 'lucide-react';
import { useState } from 'react';
import {
  createDecision,
  fetchAgentsRegistry,
  fetchSystemHealth,
  listDecisions,
  listProposals,
} from '../api/queries';
import type {
  AgentsRegistryResponse,
  Decision,
  Proposal,
} from '../api/types';
import { NewProposalModal } from '../components/governance/NewProposalModal';
import { fallbackAgents, fallbackHealth } from '../data/fallbacks';
import { useSCPStream } from '../hooks/useSCPStream';
import useCockpitStore from '../state/cockpitStore';

export default function CockpitPage() {
  const router = useRouter();
  const { activeAgentId } = useCockpitStore();
  const { timeline, connection } = useSCPStream();
  const [toast, setToast] = useState<string | null>(null);
  const [isProposalModalOpen, setProposalModalOpen] = useState(false);

  // Queries
  const agentsQuery = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
    retry: 1,
    initialData: { agents: fallbackAgents },
  });

  const { data: healthData } = useQuery({
    queryKey: ['system-health'],
    queryFn: fetchSystemHealth,
    retry: 1,
    staleTime: 30_000,
    initialData: fallbackHealth,
  });

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

  const agents = agentsQuery.data?.agents ?? fallbackAgents;

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
        setToast('تم تسجيل القرار بنجاح');
      })
      .catch((err) => setToast(err?.message || 'تعذر تسجيل القرار'));
  };

  return (
    <div className="space-y-6">
      {toast && (
        <div className="fixed top-3 right-3 z-50 px-4 py-2 rounded-lg bg-emerald-600 text-white shadow-panel text-sm animate-in fade-in slide-in-from-top-4">
          {toast}
          <button className="ml-2 text-xs underline" onClick={() => setToast(null)}>
            إغلاق
          </button>
        </div>
      )}

      <header className="glass rounded-3xl p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row gap-6 lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.15em] text-brand-base font-semibold">
              ICGL COCKPIT · RTL
            </p>
            <h1 className="text-3xl font-extrabold text-ink mt-2 leading-tight">
              لوحة القيادة التنفيذية
              <span className="text-brand-base"> · Executive Overview</span>
            </h1>
            <p className="text-sm text-slate-600 mt-2 max-w-2xl">
              نظرة عامة على حالة السيادة، أداء الوكلاء، والقرارات المعلقة. استخدم القائمة الجانبية للغوص في الأقسام التخصصية.
            </p>
            <div className="flex items-center gap-3 mt-6">
              <button
                onClick={() => router.navigate({ to: '/chat' })}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-base text-white shadow-lg shadow-brand-base/20 hover:bg-brand-deep hover:scale-105 active:scale-95 transition-all text-sm font-bold"
              >
                <Bot className="w-4 h-4" />
                المساعد الذكي (Chat)
              </button>
              <button
                onClick={() => router.navigate({ to: '/chat' })} // Terminal is inside ChatPage
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all text-sm font-bold"
              >
                <code className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">CTRL+T</code>
                التيرمنال (Terminal)
              </button>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 min-w-[280px]">
            <MetricTile
              title="Agents Live"
              value={healthData?.active_agents ?? agents.length}
              caption="active"
              icon={<Bot className="w-5 h-5" />}
            />
            <MetricTile
              title="Integrity"
              value={`${healthData?.integrity_score ?? 90}%`}
              caption={healthData?.status || 'normal'}
              icon={<Shield className="w-5 h-5" />}
            />
            <MetricTile
              title="Workflows"
              value={healthData?.active_operations ?? 0}
              caption="executing"
              icon={<Workflow className="w-5 h-5" />}
            />
            <MetricTile
              title="SCP State"
              value={connection === 'open' ? 'Live' : 'Syncing'}
              caption="Real-time Stream"
              icon={<Globe2 className="w-5 h-5" />}
            />
          </div>
        </div>
      </header>

      <section className="grid lg:grid-cols-2 gap-6">
        {/* Proposal Overview */}
        <div className="glass rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-ink flex items-center gap-2">
              <FileText className="w-5 h-5 text-brand-base" />
              المقترحات المعلقة
            </h3>
            <button
              className="px-3 py-1.5 rounded-xl bg-brand-soft text-brand-base text-xs font-bold hover:bg-brand-base hover:text-white transition-colors"
              onClick={() => setProposalModalOpen(true)}
            >
              مقترح جديد +
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
                    {p.state} · {p.reason.slice(0, 50)}...
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
            {timeline.slice(0, 6).map((event, idx) => (
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
            {timeline.length === 0 && (
              <div className="text-center py-10 text-slate-400">
                <Clock className="w-8 h-8 mx-auto mb-2 opacity-10" />
                <p className="text-sm">بانتظار الأحداث المباشرة...</p>
              </div>
            )}
          </div>
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

function MetricTile({
  title,
  value,
  caption,
  icon,
}: {
  title: string;
  value: string | number;
  caption: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-white/50 p-4 rounded-2xl border border-slate-100 shadow-sm">
      <div className="flex items-center gap-2 text-slate-400 mb-1">
        {icon}
        <span className="text-[10px] font-bold uppercase tracking-wider">{title}</span>
      </div>
      <p className="text-xl font-black text-ink">{value}</p>
      <p className="text-[9px] text-slate-500 uppercase font-medium mt-0.5">{caption}</p>
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
