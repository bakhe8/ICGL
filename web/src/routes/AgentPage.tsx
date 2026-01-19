import type React from 'react';
import { useEffect, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from '@tanstack/react-router';
import {
  ArrowRight,
  BadgeCheck,
  CheckCircle2,
  Github,
  GitPullRequest,
  ShieldCheck,
  Signal,
  Siren,
  Workflow,
} from 'lucide-react';
import { fetchAgentsRegistry } from '../api/queries';
import type { AgentRunResult, AgentsRegistryResponse } from '../api/types';
import { fallbackAgents } from '../data/fallbacks';
import { useSCPStream } from '../hooks/useSCPStream';
import { runAgent, listProposals } from '../api/queries';
import { createProposal, createConflict, createDecision } from '../api/queries';
import type { Proposal } from '../api/types';

export default function AgentPage() {
  const router = useRouter();
  const { agentId } = useParams({ from: '/agent/$agentId' });
  const { connection } = useSCPStream();

  const { data } = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
    initialData: { agents: fallbackAgents },
  });
  const proposalsQuery = useQuery<{ proposals: Proposal[] }>({
    queryKey: ['proposals'],
    queryFn: () => listProposals(),
    staleTime: 5_000,
  });

  const agent = data?.agents.find((a) => a.id === agentId) || fallbackAgents[0];
  const isEngineer = agentId === 'engineer';
  const isSentinel = agentId === 'sentinel';

  const canRunAgent = Boolean(
    agent.role &&
      ['architect', 'builder', 'policy', 'sentinel', 'guardian', 'secretary', 'archivist', 'development_manager'].includes(
        agent.role,
      ),
  );

  const runMutation = useMutation<AgentRunResult, Error>({
    mutationKey: ['run-agent', agentId],
    mutationFn: () =>
      runAgent(agent.role || agent.id, {
        title: `تشغيل ${agent.name}`,
        context: `تشغيل مباشر من لوحة Cockpit للوكيل ${agent.name} (${agent.department})`,
      }),
  });

  useEffect(() => {
    runMutation.reset();
  }, [agentId]);

  const [selectedProposalId, setSelectedProposalId] = useState<string | undefined>(undefined);
  useEffect(() => {
    if (!selectedProposalId && proposalsQuery.data?.proposals?.length) {
      setSelectedProposalId(proposalsQuery.data.proposals[0].id);
    }
  }, [proposalsQuery.data, selectedProposalId]);

  const submitDecision = async (decision: 'approved' | 'rejected' | 'deferred') => {
    if (!runMutation.data) return;
    const rationale = `Decision from ${agent.name} screen`;
    const baseProposalId = selectedProposalId;
    if (baseProposalId) {
      await createDecision({ proposal_id: baseProposalId, decision, rationale });
      proposalsQuery.refetch();
      return;
    }
    const res = await createProposal({
      title: `اقتراح من الوكيل ${agent.name}`,
      description: runMutation.data?.analysis || '',
      reason: 'ناتج تشغيل وكيل',
      impact: 'مطلوب تقييم من الحوكمة',
      risks: runMutation.data.concerns.join('; ') || 'غير محدد',
      consultation_notes: runMutation.data.recommendations.join('; '),
    });
    const pid = res.proposal.id;
    setSelectedProposalId(pid);
    await createDecision({ proposal_id: pid, decision, rationale });
    proposalsQuery.refetch();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm">
        <button
          className="flex items-center gap-1 text-brand-base font-semibold"
          onClick={() => router.navigate({ to: '/' })}
        >
          <ArrowRight className="w-4 h-4" />
          رجوع
        </button>
        <span className="text-slate-400">/</span>
        <span className="text-slate-600">{agent.department}</span>
      </div>

      <section className="glass rounded-3xl p-6 space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs text-slate-500">{agent.department}</p>
            <h2 className="text-2xl font-bold text-ink">{agent.name}</h2>
            <p className="text-sm text-slate-600 mt-1">{agent.description}</p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-semibold">
            <span className="px-3 py-1 rounded-full bg-brand-soft text-brand-base border border-brand-base/20">
              {agent.status === 'active' ? 'Live' : agent.fidelity === 'roadmap' ? 'Roadmap' : 'Mock'}
            </span>
            <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 border">
              {agent.fidelity}
            </span>
            <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 border">
              {connection === 'open' ? 'SCP Connected' : 'SCP Simulated'}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {canRunAgent && (
            <button
              className="px-3 py-2 rounded-xl bg-brand-base text-white text-sm flex items-center gap-2 shadow-sm"
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
            >
              <CheckCircle2 className="w-4 h-4" />
              {runMutation.isPending ? 'تشغيل...' : 'تشغيل الوكيل الآن'}
            </button>
          )}
          <span className="px-3 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm border">
            role: {agent.role || 'غير متصل'}
          </span>
        </div>

        {runMutation.isError && (
          <div className="p-3 rounded-xl border border-rose-200 bg-rose-50 text-sm text-rose-800">
            فشل التشغيل: {runMutation.error.message}
          </div>
        )}

        {runMutation.data && (
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 space-y-2 text-sm">
            <div className="flex items-center gap-2 text-emerald-800">
              <CheckCircle2 className="w-4 h-4" />
              <p className="font-semibold">نتيجة الوكيل · {runMutation.data.role}</p>
            </div>
            <p className="text-ink font-semibold">{runMutation.data.analysis}</p>
            <div className="flex flex-wrap gap-2">
              {runMutation.data.recommendations.map((rec) => (
                <span key={rec} className="px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-800">
                  {rec}
                </span>
              ))}
            </div>
            {runMutation.data.concerns.length > 0 && (
              <div className="text-rose-700">
                <p className="font-semibold text-xs">Concerns</p>
                <ul className="list-disc pr-4">
                  {runMutation.data.concerns.map((c) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              </div>
            )}
            {runMutation.data.references && runMutation.data.references.length > 0 && (
              <div className="text-xs text-slate-700 bg-white/70 border border-slate-200 rounded-xl p-2">
                <p className="font-semibold text-slate-800 mb-1">References</p>
                <pre className="whitespace-pre-wrap max-h-40 overflow-y-auto">{runMutation.data.references.join('\n')}</pre>
              </div>
            )}
            <div className="flex gap-2 text-xs">
              <button
                className="px-3 py-1.5 rounded-lg bg-brand-base text-white"
                onClick={() =>
                  createProposal({
                    title: `اقتراح من الوكيل ${agent.name}`,
                    description: runMutation.data?.analysis || '',
                    reason: 'ناتج تشغيل وكيل',
                    impact: 'مطلوب تقييم من الحوكمة',
                    risks: runMutation.data.concerns.join('; ') || 'غير محدد',
                    consultation_notes: runMutation.data.recommendations.join('; '),
                  })
                }
              >
                إنشاء مقترح
              </button>
              <button
                className="px-3 py-1.5 rounded-lg bg-amber-500 text-white"
                onClick={() =>
                  createConflict({
                    title: `تعارض/ملاحظة من ${agent.name}`,
                    description: runMutation.data?.analysis || '',
                    involved_agents: [agent.id],
                  })
                }
              >
                تسجيل تعارض
              </button>
            </div>
            <div className="flex flex-wrap gap-2 text-xs items-center">
              <div className="flex items-center gap-2">
                <span className="text-slate-600">ربط القرار بالمقترح:</span>
                <select
                  className="px-2 py-1 rounded border border-slate-300"
                  value={selectedProposalId || ''}
                  onChange={(e) => setSelectedProposalId(e.target.value || undefined)}
                >
                  <option value="">(إنشاء مقترح جديد تلقائياً)</option>
                  {(proposalsQuery.data?.proposals || []).map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title} · {p.state}
                    </option>
                  ))}
                </select>
              </div>
              <button
                className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white"
                disabled={!runMutation.data}
                onClick={() => submitDecision('approved')}
              >
                تسجيل قرار (موافقة)
              </button>
              <button
                className="px-3 py-1.5 rounded-lg bg-rose-600 text-white"
                disabled={!runMutation.data}
                onClick={() => submitDecision('rejected')}
              >
                تسجيل قرار (رفض)
              </button>
              <button
                className="px-3 py-1.5 rounded-lg bg-amber-500 text-white"
                disabled={!runMutation.data}
                onClick={() => submitDecision('deferred')}
              >
                تسجيل قرار (تأجيل)
              </button>
            </div>
          </div>
        )}

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {agent.capabilities.map((cap) => (
            <div
              key={cap}
              className="p-3 rounded-xl border border-slate-200 bg-white/80 text-sm flex items-start gap-2"
            >
              <CheckCircle2 className="w-4 h-4 text-brand-base mt-0.5" />
              <div>
                <p className="font-semibold text-ink">{cap}</p>
                <p className="text-xs text-slate-600">نشط عبر Cockpit</p>
              </div>
            </div>
          ))}
        </div>

        <div className="glass rounded-2xl p-4 border border-slate-100 space-y-2">
          <p className="text-xs text-slate-500">Signals</p>
          <div className="flex flex-wrap gap-2 text-[11px]">
            {(agent.signals || ['No live signals']).map((signal) => (
              <span
                key={signal}
                className="px-2 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700"
              >
                {signal}
              </span>
            ))}
          </div>
        </div>
      </section>

      {isEngineer && <EngineerGitOps />}
      {isSentinel && <SentinelPanel />}
    </div>
  );
}

function EngineerGitOps() {
  return (
    <section className="glass rounded-3xl p-6 space-y-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-xs text-slate-500">GitOps Dashboard</p>
          <h3 className="font-semibold text-ink">مهندس · GitOps / Version Control</h3>
        </div>
        <Github className="w-5 h-5 text-brand-base" />
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <GitOpsTile title="Main Branch" value="Protected" badge="No drift" icon={<ShieldCheck />} />
        <GitOpsTile title="Deploy Window" value="Green" badge="No blockers" icon={<BadgeCheck />} />
        <GitOpsTile title="Open PRs" value="4" badge="2 need review" icon={<GitPullRequest />} />
        <GitOpsTile title="Pipelines" value="11/11 passed" badge="CI stable" icon={<Workflow />} />
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white/80 p-4 space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <Signal className="w-4 h-4 text-brand-base" />
          <p className="font-semibold text-ink">GitOps Status</p>
        </div>
        <p className="text-slate-600">
          مراقبة فروع الإنتاج، مراجعة حواجز النشر (progressive delivery)، والتحقق من تطابق السياسات مع
          ملفات IaC. هذا اللوحة Mock عالية الدقة وقابلة للترقية إلى مصدر بيانات حقيقي.
        </p>
      </div>
    </section>
  );
}

function SentinelPanel() {
  return (
    <section className="glass rounded-3xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-500">Sentinel</p>
          <h3 className="font-semibold text-ink">Drift Monitor · Pattern Alerts</h3>
        </div>
        <Siren className="w-5 h-5 text-amber-600" />
      </div>
      <div className="grid sm:grid-cols-2 gap-3 text-sm">
        <div className="p-3 rounded-xl border border-amber-200 bg-amber-50">
          <p className="font-semibold text-amber-900">Drift Monitor</p>
          <p className="text-xs text-amber-800 mt-1">Live feed via /ws/scp (imperial blue overlay)</p>
        </div>
        <div className="p-3 rounded-xl border border-emerald-200 bg-emerald-50">
          <p className="font-semibold text-emerald-900">Pattern Alerts</p>
          <p className="text-xs text-emerald-800 mt-1">Aggregated signals + HDAL decisions</p>
        </div>
      </div>
    </section>
  );
}

function GitOpsTile({
  title,
  value,
  badge,
  icon,
}: {
  title: string;
  value: string;
  badge: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="p-3 rounded-2xl border border-slate-200 bg-white/80 flex flex-col gap-1">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        {icon}
        <span>{title}</span>
      </div>
      <div className="text-lg font-bold text-ink">{value}</div>
      <p className="text-[11px] text-slate-500">{badge}</p>
    </div>
  );
}
