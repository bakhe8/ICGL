import React from "react";

export type CapabilityGap = { name: string; priority: string };

export type CapabilityGapGroup = {
  critical: CapabilityGap[];
  medium: CapabilityGap[];
  enhancement: CapabilityGap[];
};

export type TechnicalAgent = {
  id?: string;
  name: string;
  role?: string;
  status?: string;
  description?: string;
};

export interface TechnicalCapabilitiesProps {
  agents: TechnicalAgent[];
  gaps: CapabilityGapGroup;
  isAgentsLoading?: boolean;
  isGapsLoading?: boolean;
}

const Badge = ({ label }: { label: string }) => (
  <span className="px-2 py-1 rounded-full text-[11px] bg-indigo-50 text-indigo-700 border border-indigo-100 shadow-sm">
    {label}
  </span>
);

export const TechnicalCapabilities: React.FC<TechnicalCapabilitiesProps> = ({
  agents,
  gaps,
  isAgentsLoading,
  isGapsLoading,
}) => {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">Sovereign Intel</p>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Active Agents & Capability Gaps</h1>
        <p className="text-sm text-slate-500 max-w-2xl leading-relaxed">
          Real-time registry of {agents.length || "..."} active agents and their specialized domains, synchronized with the Iterative Co-Governance Loop.
        </p>
      </header>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest">Registry Hub (Live)</h2>
          {isAgentsLoading && <span className="text-[10px] text-indigo-400 animate-pulse">Synchronizing...</span>}
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <div
              key={agent.id || agent.name}
              className="group rounded-2xl border border-slate-200 bg-white/50 backdrop-blur-sm p-5 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all duration-300"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="text-[9px] font-black text-slate-400 uppercase tracking-tighter mb-1">{agent.role || "Agent"}</p>
                  <h3 className="text-lg font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">{agent.name}</h3>
                </div>
                <Badge label={agent.status || "active"} />
              </div>
              <p className="text-sm text-slate-500 mt-2 line-clamp-2 leading-relaxed">{agent.description || "No description provided."}</p>
            </div>
          ))}
          {!agents.length && !isAgentsLoading && (
            <div className="col-span-full py-12 text-center rounded-2xl border-2 border-dashed border-slate-200">
              <p className="text-sm text-slate-400 italic">No agents found in registry.</p>
            </div>
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-black text-amber-600 uppercase tracking-widest">Growth Horizons (Gaps)</h2>
          {isGapsLoading && <span className="text-[10px] text-amber-500 animate-pulse">Analyzing...</span>}
        </div>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <GapColumn title="Critical" color="text-red-600" items={gaps.critical} />
          <GapColumn title="Medium" color="text-amber-600" items={gaps.medium} />
          <GapColumn title="Future" color="text-emerald-600" items={gaps.enhancement} />
        </div>
      </section>
    </div>
  );
};

function GapColumn({ title, color, items }: { title: string; color: string; items: CapabilityGap[] }) {
  return (
    <div className="rounded-xl bg-white/70 backdrop-blur-md border border-slate-200 p-4 shadow-sm space-y-3">
      <div className={`text-[10px] font-black uppercase tracking-widest flex items-center gap-2 ${color}`}>
        <span className={`w-1.5 h-1.5 rounded-full current-color bg-current`}></span>
        {title}
      </div>
      {items.length ? (
        <ul className="space-y-2 text-slate-600">
          {items.map((gap) => (
            <li key={gap.name} className="flex items-center justify-between text-xs py-1.5 border-b border-slate-50 last:border-0">
              <span className="font-semibold">{gap.name}</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-400 font-bold uppercase">{gap.priority}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-xs text-slate-300 italic py-2">No gaps identified.</div>
      )}
    </div>
  );
}
