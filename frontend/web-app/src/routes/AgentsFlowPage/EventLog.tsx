
export type EventInfo = {
    time: string;
    agent: string;
    description: string;
    type: string;
};

const EventLog = ({ events }: { events: EventInfo[] }) => {
    const list = events || [];
    return (
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm max-h-80 overflow-y-auto">
            <h2 className="font-semibold text-slate-800 mb-2">سجل الأحداث</h2>
            {list.length === 0 ? (
                <p className="text-sm text-slate-500">لا توجد أحداث مسجلة بعد.</p>
            ) : (
                <ul className="space-y-2">
                    {list.map((ev, idx) => (
                        <li key={idx} className="flex flex-col gap-1 text-sm p-2 rounded-xl bg-slate-50">
                            <div className="flex items-center gap-2 text-slate-500 text-xs">
                                <span>{ev.time || '—'}</span>
                                <span>•</span>
                                <span className="font-bold text-slate-700">{ev.agent}</span>
                                <span className={`px-2 py-0.5 rounded-full text-xs ${ev.type === 'success' ? 'bg-green-100 text-green-700' : ev.type === 'warning' ? 'bg-yellow-100 text-yellow-700' : ev.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-slate-200 text-slate-700'}`}>{ev.type}</span>
                            </div>
                            <div className="text-slate-800">{ev.description}</div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default EventLog;
