
import { useEffect, useState } from 'react';
import { resolveWsUrl } from '../../../shared/client';
import { useWebSocket } from '../../../shared/hooks/useWebSocket';

interface ObservabilityEvent {
    event_type: string;
    actor_id: string;
    action: string;
    status: string;
    timestamp: string;
    target?: string;
    error_message?: string;
}

const SCPEvents = () => {
    const [events, setEvents] = useState<ObservabilityEvent[]>([]);
    const wsUrl = resolveWsUrl('/api/system/live');
    const { lastMessage } = useWebSocket(wsUrl);

    useEffect(() => {
        if (lastMessage?.type === 'event') {
            const eventData = lastMessage.data as ObservabilityEvent;
            // Validate eventData before state update to prevent 'undefined' in array
            if (eventData && eventData.status) {
                // Use setTimeout to move state update out of the synchronous render/effect execution loop
                setTimeout(() => {
                    setEvents(prev => [eventData, ...prev].slice(0, 100));
                }, 0);
            }
        }
    }, [lastMessage]);

    return (
        <div className="h-full flex flex-col gap-4 animate-in fade-in duration-500">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-800">📡 Real-Time Event Stream</h3>
                <span className="px-2 py-1 rounded-lg bg-indigo-50 text-indigo-600 text-[10px] font-black">{events.length} Events Buffering</span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin">
                {events.length === 0 && (
                    <div className="h-40 flex flex-col items-center justify-center text-slate-400">
                        <div className="w-8 h-8 rounded-full border-2 border-slate-200 border-t-indigo-500 animate-spin mb-4" />
                        <p className="text-xs font-medium">Listening for network signals...</p>
                    </div>
                )}
                {events.map((event, idx) => (
                    event ? (
                        <div key={idx} className={`p-4 rounded-2xl border transition-all ${event?.status === 'failure' ? 'bg-red-50 border-red-100' : 'bg-slate-50 border-slate-100'
                            }`}>
                            <div className="flex justify-between items-start mb-2">
                                <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest ${event.status === 'failure' ? 'bg-red-200 text-red-700' : 'bg-indigo-100 text-indigo-700'
                                    }`}>
                                    {event.event_type}
                                </span>
                                <span className="text-[10px] font-mono text-slate-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-xs">
                                <div>
                                    <span className="text-slate-400 block mb-0.5">Actor</span>
                                    <span className="font-bold text-slate-700">{event.actor_id}</span>
                                </div>
                                <div>
                                    <span className="text-slate-400 block mb-0.5">Action</span>
                                    <span className="font-bold text-slate-700">{event.action}</span>
                                </div>
                            </div>
                            {event.error_message && (
                                <div className="mt-2 p-2 rounded-lg bg-red-100/50 text-[10px] text-red-600 font-bold font-mono">
                                    ❌ {event.error_message}
                                </div>
                            )}
                        </div>
                    ) : null
                ))}
            </div>
        </div>
    );
};

export default SCPEvents;
