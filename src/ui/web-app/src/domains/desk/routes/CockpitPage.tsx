import { ExecutiveConsole } from '../../../shared/features/executive/ExecutiveConsole';
import { CouncilGrid } from '../../../shared/features/governance/CouncilGrid';
import { CouncilPulse } from '../../../shared/features/governance/CouncilPulse';

import { useQuery } from '@tanstack/react-query';
import { Shield } from 'lucide-react';
import { fetchAgentsRegistry, fetchSystemHealth } from '../../../shared/api/system';
import { fetchJson } from '../../../shared/client';
import { useGovernanceStream } from '../../../shared/hooks/useGovernanceStream';
import type { SystemHealth } from '../../../shared/types';
import type { AgentsRegistryResponse } from '../../hall/types';

export default function CockpitPage() {
  const { status } = useGovernanceStream();


  const agentsQuery = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 60_000,
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
  const agents = agentsQuery.data?.agents ?? [];

  return (
    <div className="space-y-8 pt-6 pb-20 relative">
      <section className="relative overflow-hidden rounded-[2.5rem] p-8 glass-panel sovereign-glow bg-gradient-to-br from-brand-primary/10 to-transparent">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-1">
            <h2 className="text-3xl font-black text-slate-900 flex items-center gap-3">
              <Shield className="w-8 h-8 text-brand-primary animate-pulse" />
              Sovereign Cockpit Baseline
            </h2>
            <p className="text-slate-500 font-medium">Production Stability Verified</p>
          </div>
        </div>
        <CouncilPulse consultations={activeTraffic.length > 0 ? activeTraffic : [
          { from: 'system', to: 'idle', type: 'pulse' }
        ]} />
      </section>

      <div className="grid lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 space-y-6">
          <ExecutiveConsole />
        </div>
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-3xl bg-white border border-slate-200">
            <h3 className="font-bold mb-4">System Status</h3>
            <p className="text-sm text-slate-500">Health: {healthQuery.data?.status || 'OPTIMAL'}</p>
            <p className="text-sm text-slate-500">Pulse: {status}</p>
          </div>
        </div>
        <section className="glass-panel rounded-[2.5rem] p-8 space-y-8 w-full lg:col-span-12">
          <CouncilGrid agents={agents} />
        </section>
      </div>
    </div>
  );
}
