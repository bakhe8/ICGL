
interface AgentEvent {
    id: string;
    type: 'proposal' | 'decision' | 'conflict';
    title: string;
    subtitle: string;
    timestamp: string;
    targetId?: string;
}

interface AgentHistoryProps {
    events: AgentEvent[];
}

export function AgentHistory({ events }: AgentHistoryProps) {
    return (
        <div className="space-y-2 text-xs">
            {events.map((evt) => (
                <div
                    key={`${evt.type}-${evt.id}`}
                    className="p-3 rounded-xl border border-slate-200 bg-white/80 flex items-center gap-3 shadow-sm"
                >
                    <span
                        className={`px-2 py-0.5 rounded-full border text-[11px] font-medium ${evt.type === 'proposal'
                            ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
                            : evt.type === 'decision'
                                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                                : 'bg-amber-50 text-amber-800 border-amber-200'
                            }`}
                    >
                        {evt.type === 'proposal' ? 'مقترح' : evt.type === 'decision' ? 'قرار' : 'تعارض'}
                    </span>
                    <div className="flex-1">
                        <div className="font-semibold text-slate-800">{evt.title}</div>
                        <div className="text-slate-600">{evt.subtitle}</div>
                    </div>
                    <span className="text-slate-400 text-[10px]">{evt.timestamp}</span>
                </div>
            ))}
            {events.length === 0 && (
                <div className="p-4 rounded-xl border border-dashed border-slate-200 text-slate-500 text-center">
                    لا يوجد سجل بعد لهذا الوكيل.
                </div>
            )}
        </div>
    );
}
