import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import {
  Building2,
  Cog,
  Files,
  Gavel,
  GraduationCap,
  Layout,
  MessageSquare,
  Share2,
  ShieldCheck,
  Users
} from 'lucide-react';
import type { ElementType } from 'react';
import { fetchAgentsRegistry } from '../api/queries';
import type { AgentRegistryEntry, AgentsRegistryResponse } from '../api/types';
import { fallbackAgents } from '../data/fallbacks';
import useCockpitStore from '../state/cockpitStore';

const sections: { id: string; title: string; icon: ElementType; items: string[]; to: string }[] = [
  { id: 'executive', title: 'المكتب التنفيذي', icon: Building2, items: ['secretary'], to: '/' },
  { id: 'engineering', title: 'الهندسة', icon: Layout, items: ['architect'], to: '/ops' },
  { id: 'governance', title: 'الحوكمة', icon: Gavel, items: ['policy', 'hdal'], to: '/' },
  { id: 'archive', title: 'الأرشيف السيادي', icon: Files, items: ['archivist'], to: '/mind' },
  { id: 'extended_mind', title: 'الذاكرة الممتدة', icon: Share2, items: [], to: '/mind/graph' },
  { id: 'operations', title: 'العمليات', icon: Cog, items: ['builder', 'engineer'], to: '/operations' },
  { id: 'security', title: 'الأمن', icon: ShieldCheck, items: ['sentinel', 'guardian', 'monitor'], to: '/security' },
  { id: 'hr', title: 'الموارد البشرية', icon: Users, items: ['hr'], to: '/' },
  { id: 'roadmap', title: 'Roadmap', icon: GraduationCap, items: ['scholar', 'cartographer'], to: '/roadmap' },
  { id: 'communication', title: 'الاتصال', icon: MessageSquare, items: ['chat'], to: '/chat' },
];

const statusColor: Record<string, string> = {
  active: 'bg-brand-soft text-brand-base border border-brand-base/20',
  mock: 'bg-amber-50 text-amber-700 border border-amber-200',
};

export default function OrgSidebar() {
  const { activeAgentId, setActiveAgent } = useCockpitStore();
  const { data } = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
    retry: 1,
    initialData: { agents: fallbackAgents },
  });

  const byId = new Map(data?.agents.map((a: AgentRegistryEntry) => [a.id, a]));

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
        {sections.map(({ id, title, icon: Icon, items, to }) => (
          <div key={id} className="rounded-xl border border-slate-200/80 bg-white/70">
            <Link
              to={to}
              className="w-full px-3 py-2.5 flex items-center gap-3 text-right hover:bg-brand-soft/30 transition-colors"
              activeProps={{ className: 'bg-brand-soft/50' }}
            >
              <Icon className="w-4 h-4 text-brand-base" />
              <span className="text-sm font-semibold text-ink">{title}</span>
            </Link>
            <div className="px-3 pb-3 space-y-2">
              {items.map((agentId) => {
                const agent = byId.get(agentId) as AgentRegistryEntry | undefined;
                if (!agent) return null;
                const active = activeAgentId === agentId;
                return (
                  <Link
                    key={agentId}
                    to="/agent/$agentId"
                    params={{ agentId }}
                    className={`block p-3 rounded-lg border transition cursor-pointer ${active
                      ? 'border-brand-base bg-brand-soft/60 shadow-sm'
                      : 'border-slate-200 hover:border-brand-base/60'
                      }`}
                    onClick={() => setActiveAgent(agentId)}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-semibold text-ink">{agent.name}</div>
                      <span className={`text-[11px] px-2 py-1 rounded-full ${statusColor[agent.status]}`}>
                        {agent.fidelity === 'roadmap' ? 'Roadmap' : agent.status === 'active' ? 'Live' : 'Mock'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{agent.description}</p>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
