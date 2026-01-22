
export type EventInfo = {
    time: string;
    agent: string;
    description: string;
    type: string;
};

const EventLog = ({ events }: { events: EventInfo[] }) => (
    <div className="bg-gray-50 rounded p-4 mb-6 max-h-64 overflow-y-auto">
        <h2 className="font-semibold text-gray-700 mb-2">سجل الأحداث</h2>
        <ul className="space-y-2">
            {events.map((ev, idx) => (
                <li key={idx} className="flex gap-3 items-center text-sm">
                    <span className="text-gray-400">{ev.time}</span>
                    <span className="font-bold text-blue-700">{ev.agent}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${ev.type === 'success' ? 'bg-green-100 text-green-700' : ev.type === 'warning' ? 'bg-yellow-100 text-yellow-700' : ev.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}`}>{ev.type}</span>
                    <span className="text-gray-700">{ev.description}</span>
                </li>
            ))}
        </ul>
    </div>
);

export default EventLog;
