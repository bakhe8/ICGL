import React from "react";
import { Bot, ChevronRight } from "lucide-react";

export type CouncilAgent = {
  id: string;
  name: string;
  status?: string;
  department?: string;
};

export interface CouncilGridProps {
  agents: CouncilAgent[];
  onSelect?: (agentId: string) => void;
}

export const CouncilGrid: React.FC<CouncilGridProps> = ({ agents, onSelect }) => {
  if (!agents || agents.length === 0) {
    return (
      <div className="p-8 text-center border border-dashed border-slate-700 rounded-3xl">
        <p className="text-slate-500 font-medium">No agents active in the registry.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-6 p-2">
      {agents.map((agent) => (
        <div
          key={agent.id}
          onClick={() => onSelect?.(agent.id)}
          className="group relative bg-slate-900 border border-slate-800 rounded-3xl p-6 hover:border-brand-primary/50 transition-all cursor-pointer shadow-lg hover:shadow-brand-primary/10 flex flex-col h-full min-h-[180px]"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-all">
              <Bot className="w-6 h-6" />
            </div>
            <div className="flex flex-col items-end">
              <span
                className={`w-2 h-2 rounded-full mb-1 ${
                  agent.status === "active" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-slate-700"
                }`}
              />
              <span className="text-[9px] font-black text-slate-500 uppercase tracking-tighter">
                {agent.status || "OFFLINE"}
              </span>
            </div>
          </div>

          <div className="space-y-1 flex-1">
            <h4 className="text-white font-bold text-lg group-hover:text-brand-primary transition-colors truncate">
              {agent.name}
            </h4>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest truncate">
              {agent.department || "Consensus Unit"}
            </p>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <div className="flex -space-x-2 rtl:space-x-reverse">
              {[1, 2].map((i) => (
                <div key={i} className="w-6 h-6 rounded-full border-2 border-slate-900 bg-slate-800" />
              ))}
            </div>
            <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-brand-primary group-hover:translate-x-1 rtl:group-hover:-translate-x-1 transition-all" />
          </div>

          <div className="absolute inset-0 rounded-3xl bg-brand-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        </div>
      ))}
    </div>
  );
};
