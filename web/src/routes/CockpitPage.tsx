import type React from 'react';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import {
  Activity,
  ArrowLeftRight,
  BookOpen,
  Bot,
  CheckCircle2,
  CircleDot,
  FileText,
  GitBranch,
  Globe2,
  Shield,
  Workflow,
  FileSearch,
  Play,
} from 'lucide-react';
import {
  fetchAgentsRegistry,
  fetchDocsTree,
  fetchDocContent,
  fetchPatternAlerts,
  fetchSystemHealth,
  runPatternDetection,
  listConflicts,
  listDecisions,
  listGovernanceTimeline,
} from '../api/queries';
import type {
  AgentsRegistryResponse,
  DocNode,
  DocContentResponse,
  PatternDetectionResult,
  Proposal,
  Conflict,
  Decision,
  GovernanceEvent,
} from '../api/types';
import { fallbackAgents, fallbackDocs, fallbackHealth, fallbackPatternAlerts } from '../data/fallbacks';
import { useSCPStream } from '../hooks/useSCPStream';
import useCockpitStore from '../state/cockpitStore';
import { useMutation } from '@tanstack/react-query';
import { createProposal, listProposals, createConflict, createDecision } from '../api/queries';

const panelTitles: Record<string, string> = {
  executive: 'المكتب التنفيذي',
  governance: 'الحوكمة',
  archive: 'الأرشيف السيادي',
  operations: 'العمليات',
  security: 'الأمن',
  hr: 'الموارد البشرية',
  roadmap: 'Roadmap',
};

const statusColor: Record<string, string> = {
  active: 'bg-brand-soft text-brand-base border border-brand-base/20',
  mock: 'bg-amber-50 text-amber-700 border border-amber-200',
};

function DocumentNodeItem({
  node,
  depth = 0,
  onSelect,
}: {
  node: DocNode;
  depth?: number;
  onSelect: (path: string) => void;
}) {
  const [open, setOpen] = useState(depth < 1);
  const hasChildren = node.children && node.children.length > 0;
  return (
    <div className="text-sm">
      <div
        className="flex items-center gap-2 py-1 cursor-pointer hover:text-brand-base"
        style={{ paddingRight: depth * 10 }}
        onClick={() => {
          if (hasChildren) setOpen((v) => !v);
          else onSelect(node.path);
        }}
      >
        {hasChildren ? (
          <ArrowLeftRight className={`w-3.5 h-3.5 ${open ? 'text-brand-base' : 'text-slate-400'}`} />
        ) : (
          <FileText className="w-3.5 h-3.5 text-slate-400" />
        )}
        <span>{node.name}</span>
      </div>
      {hasChildren && open && (
        <div className="pl-4 border-r border-dashed border-slate-200">
          {node.children!.map((child) => (
            <DocumentNodeItem key={child.path} node={child} depth={depth + 1} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function CockpitPage() {
  const router = useRouter();
  const { activePanel, setActivePanel, setSelectedDoc } = useCockpitStore();
  const { timeline, connection } = useSCPStream();
  const [selectedDocPath, setSelectedDocPath] = useState<string>();

  const { data: agentsData } = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
    retry: 1,
    initialData: { agents: fallbackAgents },
  });

  const { data: docsData } = useQuery({
    queryKey: ['docs-tree'],
    queryFn: fetchDocsTree,
    retry: 1,
    staleTime: 120_000,
    initialData: { roots: fallbackDocs },
  });

  const { data: docContentData } = useQuery<DocContentResponse>({
    queryKey: ['doc-content', selectedDocPath],
    queryFn: () => fetchDocContent(selectedDocPath || ''),
    enabled: Boolean(selectedDocPath),
    retry: 1,
  });

  const { data: healthData } = useQuery({
    queryKey: ['system-health'],
    queryFn: fetchSystemHealth,
    retry: 1,
    staleTime: 30_000,
    initialData: fallbackHealth,
  });

  const { data: alertsData } = useQuery({
    queryKey: ['pattern-alerts'],
    queryFn: () => fetchPatternAlerts(5),
    retry: 1,
    staleTime: 20_000,
    initialData: { alerts: fallbackPatternAlerts },
  });

  const agents = agentsData?.agents ?? fallbackAgents;
  const docs = docsData?.roots ?? fallbackDocs;
  const patternAlerts = alertsData?.alerts ?? fallbackPatternAlerts;
  const patternDetection = useMutation<PatternDetectionResult>({
    mutationFn: () => runPatternDetection(5),
  });

  const proposalsQuery = useQuery<{ proposals: Proposal[] }>({
    queryKey: ['proposals'],
    queryFn: () => listProposals(),
    staleTime: 5_000,
  });

  const conflictsQuery = useQuery<{ conflicts: Conflict[] }>({
    queryKey: ['conflicts'],
    queryFn: () => listConflicts(),
    staleTime: 5_000,
  });

  const decisionsQuery = useQuery<{ decisions: Decision[] }>({
    queryKey: ['decisions'],
    queryFn: () => listDecisions(),
    staleTime: 5_000,
  });

  const timelineQuery = useQuery<{ timeline: GovernanceEvent[] }>({
    queryKey: ['gov-timeline'],
    queryFn: () => listGovernanceTimeline(),
    staleTime: 5_000,
  });

  const proposalMutation = useMutation({
    mutationFn: () =>
      createProposal({
        title: 'مقترح سريع من الكوكبت',
        description: 'اقتراح مبادرة جديدة بناءً على مراقبة النظام.',
        reason: 'ملاحظة فجوات أو فرص تحسين',
        impact: 'تحسين وضوح الحوكمة',
        risks: 'تغيير في التدفق الحالي',
      }),
    onSuccess: () => proposalsQuery.refetch(),
  });

  const conflictMutation = useMutation({
    mutationFn: () =>
      createConflict({
        title: 'تعارض توصيات',
        description: 'كشف تضارب بين توصيات Sentinel وPolicy',
        proposals: [],
        involved_agents: ['sentinel', 'policy'],
      }),
    onSuccess: () => conflictsQuery.refetch(),
  });

  return (
    <div className="space-y-6">
      <section className="glass rounded-3xl p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row gap-6 lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.15em] text-brand-base font-semibold">
              ICGL COCKPIT · RTL
            </p>
            <h1 className="text-3xl font-extrabold text-ink mt-2 leading-tight">
              واجهة التحكم السيادية
              <span className="text-brand-base"> · Canonical Interface</span>
            </h1>
            <p className="text-sm text-slate-600 mt-2 max-w-2xl">
              مستقبل موحّد للحوكمة: المكتب التنفيذي، الحوكمة، الأرشيف، الأمن، والعمليات تحت لوحة واحدة
              مدعومة بـ TanStack Router/Query وZustand.
            </p>
            <div className="flex flex-wrap gap-2 mt-4 text-xs">
              <span className="px-3 py-1 rounded-full bg-brand-soft text-brand-base font-semibold">
                Imperial Blue
              </span>
              <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700">TanStack Router</span>
              <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700">Tailwind RTL</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 min-w-[260px]">
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
              title="Operations"
              value={healthData?.active_operations ?? 0}
              caption="active workflows"
              icon={<Workflow className="w-5 h-5" />}
            />
            <MetricTile
              title="SCP Stream"
              value={connection === 'open' ? 'Live' : 'Mock'}
              caption="WebSocket /ws/scp"
              icon={<Globe2 className="w-5 h-5" />}
            />
          </div>
        </div>
      </section>

      <section className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 glass rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">الحوكمة المباشرة</p>
              <h3 className="font-semibold text-ink">خط الأحداث / SCP Timeline</h3>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-slate-100 text-slate-700 border">
              {panelTitles[activePanel] ?? 'Cockpit'}
            </span>
          </div>
          <div className="space-y-2">
            {timeline.slice(0, 6).map((event) => (
              <div
                key={event.id}
                className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 bg-white/70"
              >
                <CircleDot className="w-3.5 h-3.5 text-brand-base" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-ink">{event.label}</p>
                  <p className="text-xs text-slate-500">
                    {new Date(event.time).toLocaleTimeString()} · {event.source || 'SCP'}
                  </p>
                </div>
                <span
                  className={`text-[11px] px-2 py-1 rounded-full ${
                    event.severity === 'critical'
                      ? 'bg-rose-50 text-rose-700'
                      : event.severity === 'warn'
                        ? 'bg-amber-50 text-amber-700'
                        : 'bg-emerald-50 text-emerald-700'
                  }`}
                >
                  {event.severity || 'info'}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Sentinel</p>
              <h3 className="font-semibold text-ink">Pattern Alerts</h3>
            </div>
            <div className="flex items-center gap-2">
              <button
                className="px-3 py-1.5 rounded-lg bg-brand-base text-white text-xs flex items-center gap-1"
                onClick={() => patternDetection.mutate()}
                disabled={patternDetection.isPending}
              >
                <Play className="w-3.5 h-3.5" />
                {patternDetection.isPending ? 'تشغيل...' : 'كشف الأنماط'}
              </button>
              <Shield className="w-4 h-4 text-brand-base" />
            </div>
          </div>
          <div className="space-y-2">
            {patternAlerts.slice(0, 4).map((alert) => (
              <div
                key={alert.alert_id}
                className="p-3 rounded-xl border border-slate-200 bg-white/80 flex flex-col gap-1"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-sm text-ink">{alert.pattern}</span>
                  <span
                    className={`text-[11px] px-2 py-1 rounded-full ${
                      alert.severity === 'high'
                        ? 'bg-rose-50 text-rose-700'
                        : 'bg-amber-50 text-amber-700'
                    }`}
                  >
                    {alert.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{alert.description}</p>
                <p className="text-[11px] text-slate-400">
                  {new Date(alert.timestamp).toLocaleTimeString()} · {alert.event_count} events
                </p>
              </div>
            ))}
            {patternDetection.data && (
              <div className="p-3 rounded-xl border border-emerald-200 bg-emerald-50 text-sm space-y-1">
                <div className="flex items-center gap-2 text-emerald-800">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>نتيجة كشف الأنماط</span>
                </div>
                <p className="text-xs text-emerald-700">
                  {patternDetection.data.alerts_found} alerts · analyzed {patternDetection.data.analyzed_events} events
                  {patternDetection.data.fallback ? ' (mock)' : ''}
                </p>
                <div className="flex flex-wrap gap-2">
                  {patternDetection.data.alerts.map((a) => (
                    <span
                      key={a.alert_id}
                      className="px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-800 text-xs"
                    >
                      {a.pattern}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="glass rounded-3xl p-5 space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs text-slate-500">العملاء / الوكلاء</p>
            <h3 className="font-semibold text-ink">تشغيل الوكلاء (Active + Mock)</h3>
          </div>
          <button
            className="px-3 py-2 rounded-xl bg-brand-base text-white text-sm flex items-center gap-2 shadow-sm"
            onClick={() => router.navigate({ to: '/agent/$agentId', params: { agentId: 'engineer' } })}
          >
            <GitBranch className="w-4 h-4" />
            GitOps Dashboard
          </button>
        </div>
        <div className="card-grid">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="border border-slate-200 rounded-2xl bg-white/80 p-4 flex flex-col gap-2 hover:border-brand-base/50 transition"
            >
              <div className="flex items-center justify-between gap-2">
                <div>
                  <p className="text-xs text-slate-500">{agent.department}</p>
                  <p className="font-semibold text-ink">{agent.name}</p>
                </div>
                <span className={`text-[11px] px-2 py-1 rounded-full ${statusColor[agent.status]}`}>
                  {agent.fidelity === 'roadmap' ? 'Roadmap' : agent.status === 'active' ? 'Live' : 'Mock'}
                </span>
              </div>
              <p className="text-sm text-slate-600">{agent.description}</p>
              <div className="flex flex-wrap gap-2 text-[11px] text-slate-600">
                {agent.capabilities.map((cap) => (
                  <span
                    key={cap}
                    className="px-2 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700"
                  >
                    {cap}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>{agent.signals?.[0] || '—'}</span>
                <button
                  className="text-brand-base font-semibold"
                  onClick={() => router.navigate({ to: '/agent/$agentId', params: { agentId: agent.id } })}
                >
                  فتح
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="grid lg:grid-cols-2 gap-4">
        <div className="glass rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Documents Workspace</p>
              <h3 className="font-semibold text-ink">الأرشيف الحي (Docs / Policies / ADR)</h3>
            </div>
            <BookOpen className="w-4 h-4 text-brand-base" />
          </div>
          <div className="max-h-[360px] overflow-y-auto pr-1">
            {docs.map((node) => (
              <DocumentNodeItem
                key={node.path}
                node={node}
                onSelect={(path) => {
                  setSelectedDocPath(path);
                  setSelectedDoc(path);
                  setActivePanel('archive');
                }}
              />
            ))}
          </div>
        </div>
        <div className="glass rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Governance Queue</p>
              <h3 className="font-semibold text-ink">مقترحات / تعارضات / قرارات</h3>
            </div>
            <div className="flex gap-2">
              <button
                className="px-3 py-1.5 rounded-lg bg-brand-base text-white text-xs"
                onClick={() => proposalMutation.mutate()}
                disabled={proposalMutation.isPending}
              >
                {proposalMutation.isPending ? '...' : 'مقترح سريع'}
              </button>
              <button
                className="px-3 py-1.5 rounded-lg bg-amber-500 text-white text-xs"
                onClick={() => conflictMutation.mutate()}
                disabled={conflictMutation.isPending}
              >
                {conflictMutation.isPending ? '...' : 'تسجيل تعارض'}
              </button>
            </div>
          </div>
          <div className="space-y-2">
            <div className="p-3 rounded-xl border border-slate-200 bg-white/80">
              <p className="text-xs text-slate-500">Proposals</p>
              <div className="flex flex-wrap gap-2 text-xs">
                {(proposalsQuery.data?.proposals || []).slice(0, 6).map((p) => (
                  <div key={p.id} className="px-2 py-1 rounded-full border bg-white text-slate-800 flex items-center gap-2">
                    <span>{p.title} · {p.state}</span>
                    <button
                      className="px-2 py-0.5 rounded bg-emerald-600 text-white"
                      onClick={() =>
                        createDecision({ proposal_id: p.id, decision: 'approved', rationale: 'Approved via cockpit', signed_by: 'operator' }).then(
                          () => {
                            proposalsQuery.refetch();
                            decisionsQuery.refetch();
                          },
                        )
                      }
                    >
                      موافقة
                    </button>
                    <button
                      className="px-2 py-0.5 rounded bg-rose-600 text-white"
                      onClick={() =>
                        createDecision({ proposal_id: p.id, decision: 'rejected', rationale: 'Rejected via cockpit', signed_by: 'operator' }).then(
                          () => {
                            proposalsQuery.refetch();
                            decisionsQuery.refetch();
                          },
                        )
                      }
                    >
                      رفض
                    </button>
                    <button
                      className="px-2 py-0.5 rounded bg-amber-500 text-white"
                      onClick={() =>
                        createDecision({ proposal_id: p.id, decision: 'deferred', rationale: 'Deferred via cockpit', signed_by: 'operator' }).then(
                          () => {
                            proposalsQuery.refetch();
                            decisionsQuery.refetch();
                          },
                        )
                      }
                    >
                      تأجيل
                    </button>
                  </div>
                ))}
                {proposalsQuery.data?.proposals?.length === 0 && <span className="text-slate-400">لا يوجد مقترحات</span>}
              </div>
            </div>
            <div className="p-3 rounded-xl border border-amber-200 bg-amber-50">
              <p className="text-xs text-amber-700">Conflicts</p>
              <div className="flex flex-wrap gap-2 text-xs">
                {(conflictsQuery.data as any)?.conflicts?.slice(0, 3)?.map((c: any) => (
                  <span key={c.id} className="px-2 py-1 rounded-full border border-amber-300 bg-white text-amber-800">
                    {c.title} · {c.state}
                  </span>
                ))}
                {(!(conflictsQuery.data as any)?.conflicts || (conflictsQuery.data as any)?.conflicts?.length === 0) && (
                  <span className="text-amber-700">لا توجد تعارضات مسجلة</span>
                )}
              </div>
            </div>
            <div className="p-3 rounded-xl border border-emerald-200 bg-emerald-50">
              <p className="text-xs text-emerald-700">Decisions</p>
              <div className="flex flex-wrap gap-2 text-xs">
                {(decisionsQuery.data?.decisions || []).slice(0, 3).map((d) => (
                  <span key={d.id} className="px-2 py-1 rounded-full border border-emerald-300 bg-white text-emerald-800">
                    {d.decision} · {d.proposal_id}
                  </span>
                ))}
                {(!decisionsQuery.data?.decisions || decisionsQuery.data?.decisions.length === 0) && (
                  <span className="text-emerald-700">لا يوجد قرارات مسجلة</span>
                )}
              </div>
            </div>
          </div>
          <div className="p-3 rounded-xl border border-slate-200 bg-white/80">
            <p className="text-xs text-slate-500">Timeline</p>
            <div className="space-y-1 text-xs max-h-48 overflow-y-auto">
              {(timelineQuery.data?.timeline || []).slice(0, 10).map((evt) => (
                <div key={evt.id} className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-slate-100 border text-slate-700">{evt.type}</span>
                  <span className="text-slate-600">
                    {new Date(evt.timestamp).toLocaleTimeString()} · {evt.payload?.proposal_id || evt.payload?.conflict_id || ''}
                  </span>
                </div>
              ))}
              {(!timelineQuery.data?.timeline || timelineQuery.data?.timeline.length === 0) && (
                <span className="text-slate-400">لا يوجد أحداث بعد</span>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="grid lg:grid-cols-3 gap-4">
        <div className="glass rounded-2xl p-4 space-y-3 lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">الموارد البشرية</p>
              <h3 className="font-semibold text-ink">Role Definitions</h3>
            </div>
            <UsersIcon />
          </div>
          <div className="grid sm:grid-cols-3 gap-3 text-sm">
            <RoleCard title="Ops Lead" desc="مسؤول عن إطلاقات GitOps والمصادقات" />
            <RoleCard title="Policy Owner" desc="إدارة وتعديل السياسات الحاكمة" />
            <RoleCard title="Archivist Steward" desc="حماية وتسلسل الأرشيف والسياسات" />
          </div>
        </div>
        <div className="glass rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Document Preview</p>
              <h3 className="font-semibold text-ink">المستند المحدد</h3>
            </div>
            <FileSearch className="w-4 h-4 text-brand-base" />
          </div>
          <div className="space-y-2 text-sm">
            {selectedDocPath ? (
              docContentData ? (
                <div className="p-3 rounded-xl border border-slate-200 bg-white/80">
                  <p className="font-semibold text-ink text-sm">{selectedDocPath}</p>
                  <pre className="mt-2 text-xs text-slate-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
                    {docContentData.content}
                  </pre>
                </div>
              ) : (
                <p className="text-xs text-slate-600">جاري تحميل المحتوى...</p>
              )
            ) : (
              <p className="text-xs text-slate-500">اختر مستنداً من الشجرة لعرضه هنا.</p>
            )}
          </div>
        </div>
      </section>
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
    <div className="p-3 rounded-2xl border border-slate-200 bg-white/80 flex flex-col gap-1">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        {icon}
        <span>{title}</span>
      </div>
      <div className="text-xl font-bold text-ink leading-tight">{value}</div>
      <p className="text-[11px] text-slate-500">{caption}</p>
    </div>
  );
}

function UsersIcon() {
  return (
    <div className="w-8 h-8 rounded-full bg-brand-soft text-brand-base grid place-items-center">
      <Activity className="w-4 h-4" />
    </div>
  );
}

function RoleCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="p-3 rounded-xl border border-slate-200 bg-white/80 h-full">
      <p className="font-semibold text-ink">{title}</p>
      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{desc}</p>
    </div>
  );
}
