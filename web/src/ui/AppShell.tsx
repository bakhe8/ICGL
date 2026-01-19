import type { ReactNode } from 'react';
import { Activity, Globe2, Radio } from 'lucide-react';
import useCockpitStore from '../state/cockpitStore';
import OrgSidebar from './OrgSidebar';

type Props = {
  children: ReactNode;
};

export default function AppShell({ children }: Props) {
  const { activeAgentId } = useCockpitStore();

  return (
    <div className="min-h-screen text-ink">
      <header className="sticky top-0 z-30 border-b border-brand-soft/70 bg-white/90 backdrop-blur">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-brand-base to-brand-deep text-white font-bold grid place-items-center shadow-panel">
              ICGL
            </div>
            <div>
              <p className="text-xs text-slate-500">ICGL Cockpit V5</p>
              <p className="font-semibold text-ink">Canonical Interface · RTL</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold">
            <span className="flex items-center gap-1 px-3 py-1 rounded-full bg-brand-soft text-brand-base border border-brand-base/20">
              <Radio className="w-4 h-4" />
              SCP Live
            </span>
            <span className="hidden sm:flex items-center gap-1 px-3 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              <Activity className="w-4 h-4" />
              {activeAgentId}
            </span>
            <span className="hidden sm:flex items-center gap-1 px-3 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              <Globe2 className="w-4 h-4" />
              RTL Official
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-6 lg:grid lg:grid-cols-[1fr_320px] gap-6">
        <main className="space-y-6">{children}</main>
        <div className="lg:order-last">
          <OrgSidebar />
        </div>
      </div>
    </div>
  );
}
