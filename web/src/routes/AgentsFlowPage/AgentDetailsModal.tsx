
const AgentDetailsModal = ({ agent, events, onClose }: { agent: string; events: Array<{ time: string; description: string }>; onClose: () => void }) => (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
        <div className="bg-white rounded shadow-lg p-6 min-w-[320px] max-w-[90vw]">
            <div className="font-bold text-lg text-blue-700 mb-2">تفاصيل الوكيل: {agent}</div>
            <ul className="space-y-2 mb-4">
                {events.map((ev, idx) => (
                    <li key={idx} className="text-sm text-gray-700">
                        <span className="text-gray-400">{ev.time}</span> — {ev.description}
                    </li>
                ))}
            </ul>
            <button onClick={onClose} className="bg-blue-100 text-blue-700 px-4 py-2 rounded">إغلاق</button>
        </div>
    </div>
);

export default AgentDetailsModal;
