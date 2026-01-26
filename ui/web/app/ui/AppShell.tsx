import { Activity, BrainCircuit, Globe2, Radio } from 'lucide-react';
import type { ReactNode } from 'react';
import TestComponent from '../components/TestComponent';
import '../components/TestComponent.css';
import useCockpitStore from '../state/cockpitStore';
import SidebarNav from './SidebarNav';

type Props = {
  children: ReactNode;
};

export default function AppShell({ children }: Props) {
  const { activeAgentId } = useCockpitStore();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-['Inter']">
      {/* Universal Header */}
      <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 px-8 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-base to-brand-deep text-white shadow-lg flex items-center justify-center">
            <BrainCircuit className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl font-black text-slate-900 tracking-tight">العقل الممتد — Extended Mind</h1>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Thought Alignment Hub • RTL</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-[10px] font-bold">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand-soft text-brand-base border border-brand-base/20">
              <Radio className="w-3 h-3 animate-pulse" />
              Neural Pulse Active
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200">
              <Activity className="w-3 h-3" />
              Agent: {activeAgentId}
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200">
              <Globe2 className="w-3 h-3" />
              Sovereign Node
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 flex max-w-[1700px] w-full mx-auto">
        {/* Unified Sidebar Navigation */}
        <aside className="w-72 border-l border-slate-200 bg-white/50 backdrop-blur-sm sticky top-20 h-[calc(100vh-80px)] overflow-y-auto hidden lg:block py-6">
          <SidebarNav />
        </aside>

        {/* Global Task/Sovereign Indicator */}
        <div className="fixed bottom-6 left-6 z-50">
          <TestComponent />
        </div>

        {/* Dynamic Content Area */}
        <main className="flex-1 p-8 overflow-x-hidden relative">
          <div className="max-w-[1200px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
