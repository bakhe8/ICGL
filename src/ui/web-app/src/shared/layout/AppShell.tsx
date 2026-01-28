import { BrainCircuit } from 'lucide-react';
import type { ReactNode } from 'react';

type Props = {
  children: ReactNode;
};

export default function AppShell({ children }: Props) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 px-8 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-base to-brand-deep text-white shadow-lg flex items-center justify-center">
            <BrainCircuit className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl font-black text-slate-900 tracking-tight">العقل الممتد — Extended Mind</h1>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Stable Baseline Build</p>
          </div>
        </div>
      </header>
      <div className="flex-1 flex max-w-[1700px] w-full mx-auto">
        <main className="flex-1 p-8 overflow-x-hidden relative">
          <div className="max-w-[1200px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
