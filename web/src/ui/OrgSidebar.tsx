import { useQuery } from '@tanstack/react-query';
import { useRouter } from '@tanstack/react-router';
import type { ElementType } from 'react';
import {
  Building2,
  Gavel,
  Files,
  ShieldCheck,
  Cog,
  Users,
  GraduationCap,
  Layout,
} from 'lucide-react';
import { fetchAgentsRegistry } from '../api/queries';
import type { AgentsRegistryResponse } from '../api/types';
import { fallbackAgents } from '../data/fallbacks';
import useCockpitStore, { type Panel } from '../state/cockpitStore';

const sections: { id: Panel; title: string; icon: ElementType; items: string[] }[] = [
  { id: 'executive', title: 'المكتب التنفيذي', icon: Building2, items: ['secretary'] },
  { id: 'engineering', title: 'الهندسة', icon: Layout, items: ['architect'] },
  { id: 'governance', title: 'الحوكمة', icon: Gavel, items: ['policy', 'hdal'] },
  { id: 'archive', title: 'الأرشيف السيادي', icon: Files, items: ['archivist'] },
  { id: 'operations', title: 'العمليات', icon: Cog, items: ['builder', 'engineer'] },
  { id: 'security', title: 'الأمن', icon: ShieldCheck, items: ['sentinel', 'guardian', 'monitor'] },
  { id: 'hr', title: 'الموارد البشرية', icon: Users, items: ['hr'] },
  { id: 'roadmap', title: 'Roadmap', icon: GraduationCap, items: ['scholar', 'cartographer'] },
];

const statusColor: Record<string, string> = {
  active: 'bg-brand-soft text-brand-base border border-brand-base/20',
  mock: 'bg-amber-50 text-amber-700 border border-amber-200',
};

export default function OrgSidebar() {
  const router = useRouter();
  const { activeAgentId, setActiveAgent, setActivePanel } = useCockpitStore();
  const { data } = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
    retry: 1,
    initialData: { agents: fallbackAgents },
  });

  const byId = new Map(data?.agents.map((a) => [a.id, a]));

  return (
    <aside className="glass rounded-2xl p-4 space-y-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-xs text-slate-500">Organizational Chart</p>
          <p className="font-semibold text-ink">ICGL Cockpit</p>
        </div>
        <span className="px-3 py-1 rounded-full bg-brand-soft text-brand-base text-xs font-semibold">
          RTL
        </span>
      </div>
      <div className="space-y-3">
        {sections.map(({ id, title, icon: Icon, items }) => (
          <div key={id} className="rounded-xl border border-slate-200/80 bg-white/70">
            <button
              type="button"
              onClick={() => setActivePanel(id)}
              className="w-full px-3 py-2.5 flex items-center gap-3 text-right"
            >
              <Icon className="w-4 h-4 text-brand-base" />
              <span className="text-sm font-semibold text-ink">{title}</span>
            </button>
            <div className="px-3 pb-3 space-y-2">
              {items.map((agentId) => {
                const agent = byId.get(agentId);
                if (!agent) return null;
                const active = activeAgentId === agentId;
                return (
                  <div
                    key={agentId}
                    className={`p-3 rounded-lg border transition cursor-pointer ${active
                      ? 'border-brand-base bg-brand-soft/60 shadow-sm'
                      : 'border-slate-200 hover:border-brand-base/60'
                      }`}
                    onClick={() => {
                      setActiveAgent(agentId);
                      router.navigate({ to: '/agent/$agentId', params: { agentId } }).catch(() => { });
                    }}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-semibold text-ink">{agent.name}</div>
                      <span className={`text-[11px] px-2 py-1 rounded-full ${statusColor[agent.status]}`}>
                        {agent.fidelity === 'roadmap' ? 'Roadmap' : agent.status === 'active' ? 'Live' : 'Mock'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{agent.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
