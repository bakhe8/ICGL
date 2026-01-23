import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAgentGaps, fetchAgentsList } from '../api/queries';

type CapabilityGapGroup = {
  critical: { name: string; priority: string }[];
  medium: { name: string; priority: string }[];
  enhancement: { name: string; priority: string }[];
};

const Badge = ({ label }: { label: string }) => (
  <span className="px-2 py-1 rounded-full text-[11px] bg-slate-100 text-slate-700 border border-slate-200">
    {label}
  </span>
);

const TechnicalCapabilities: React.FC = () => {
  const agentsQuery = useQuery({
    queryKey: ['agents-list-live'],
    queryFn: fetchAgentsList,
    staleTime: 30_000,
  });

  const gapsQuery = useQuery({
    queryKey: ['agent-gaps'],
    queryFn: fetchAgentGaps,
    staleTime: 60_000,
  });

  const agents = agentsQuery.data?.agents ?? [];
  const gaps: CapabilityGapGroup = {
    critical: gapsQuery.data?.critical ?? [],
    medium: gapsQuery.data?.medium ?? [],
    enhancement: gapsQuery.data?.enhancement ?? [],
  };

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="text-xs text-slate-500">القدرات التقنية للوكلاء</p>
        <h1 className="text-2xl font-semibold text-ink">الوكلاء النشطون والفجوات المعروفة</h1>
        <p className="text-sm text-slate-600 mt-1">
          عرض حي لـ {agents.length || '...'} وكيل نشط مع حالاتهم، بالإضافة إلى الفجوات ذات الأولوية من سجل القدرات.
        </p>
      </header>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink">الوكلاء النشطون (Live)</h2>
          {agentsQuery.isFetching && <span className="text-xs text-slate-400">تحديث...</span>}
        </div>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <div
              key={agent.id || agent.name}
              className="rounded-xl border border-slate-200 bg-white/80 p-4 shadow-sm space-y-2"
            >
              <div className="flex items-center justify-between gap-2">
                <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{agent.role}</p>
                  <h3 className="text-base font-semibold text-ink">{agent.name || agent.id}</h3>
                </div>
                <Badge label={agent.status || 'active'} />
              </div>
              <p className="text-sm text-slate-600">{agent.description || '—'}</p>
              {!!agent.capabilities?.length && (
                <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                  {agent.capabilities.slice(0, 4).map((c: string) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
          {!agents.length && !agentsQuery.isLoading && (
            <div className="col-span-full text-center text-slate-400 text-sm">لا يوجد وكلاء معروضون حالياً.</div>
          )}
        </div>
      </section>

      <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink">الفجوات والمجالات المطلوبة</h2>
          {gapsQuery.isFetching && <span className="text-xs text-amber-500">تحديث...</span>}
        </div>
        <div className="grid md:grid-cols-3 gap-3 text-sm">
          <GapColumn title="حرج" color="text-red-700" items={gaps.critical} />
          <GapColumn title="متوسط" color="text-amber-700" items={gaps.medium} />
          <GapColumn title="تحسين" color="text-emerald-700" items={gaps.enhancement} />
        </div>
      </section>
    </div>
  );
};

function GapColumn({ title, color, items }: { title: string; color: string; items: { name: string; priority: string }[] }) {
  return (
    <div className="rounded-lg bg-white/70 border border-slate-200 p-3 space-y-2">
      <div className={`text-xs font-black uppercase tracking-wide ${color}`}>{title}</div>
      {items.length ? (
        <ul className="space-y-1 text-slate-700">
          {items.map((gap) => (
            <li key={gap.name} className="flex items-center justify-between">
              <span>{gap.name}</span>
              <span className="text-[10px] text-slate-400">{gap.priority}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-xs text-slate-400">لا توجد فجوات.</div>
      )}
    </div>
  );
}

export default TechnicalCapabilities;
