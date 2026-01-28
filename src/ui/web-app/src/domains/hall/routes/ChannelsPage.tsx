
import { useCallback, useEffect, useState } from 'react';
import { fetchChannels } from '../api';

interface Channel {
    channel_id: string;
    from_agent: string;
    to_agent: string;
    status: string;
    message_count: number;
    violation_count: number;
    policy?: { name: string };
}


const SCPChannels = () => {
    const [channels, setChannels] = useState<Channel[]>([]);
    const [loading, setLoading] = useState(true);

    // ... inside SCPChannels ...

    const loadChannels = useCallback(async () => {
        try {
            const data = await fetchChannels();
            setChannels(data.channels || []);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadChannels();
        const interval = setInterval(loadChannels, 5000);
        return () => clearInterval(interval);
    }, [loadChannels]);

    return (
        <div className="h-full flex flex-col gap-4 animate-in fade-in duration-500">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-800">🔀 Virtual Channel Monitor</h3>
                <button onClick={loadChannels} className="text-xs font-bold text-indigo-600 hover:text-indigo-700">Refresh</button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto pr-2 pb-4">
                {loading && channels.length === 0 && <div className="col-span-2 text-center text-slate-400 text-xs py-10 animate-pulse">Scanning channels...</div>}
                {channels.length === 0 && !loading && <div className="col-span-2 text-center text-slate-400 text-xs py-10">No active agent channels.</div>}

                {channels.map(channel => (
                    <div key={channel.channel_id} className="p-5 rounded-3xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:shadow-xl hover:shadow-indigo-500/5 transition-all group">
                        <div className="flex justify-between items-center mb-4">
                            <div className="flex items-center gap-2">
                                <span className="p-1.5 rounded-lg bg-white border border-slate-100 text-[10px] font-black text-slate-700">{channel.from_agent}</span>
                                <span className="text-slate-300">→</span>
                                <span className="p-1.5 rounded-lg bg-white border border-slate-100 text-[10px] font-black text-slate-700">{channel.to_agent}</span>
                            </div>
                            <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-tighter ${channel.status === 'active' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-200 text-slate-500'
                                }`}>
                                {channel.status}
                            </span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 mb-4">
                            <div className="text-center">
                                <span className="text-[10px] text-slate-400 block">Messages</span>
                                <span className="font-bold text-slate-700">{channel.message_count}</span>
                            </div>
                            <div className="text-center">
                                <span className="text-[10px] text-slate-400 block">Violations</span>
                                <span className={`font-bold ${channel.violation_count > 0 ? 'text-red-500' : 'text-slate-700'}`}>{channel.violation_count}</span>
                            </div>
                            <div className="text-center">
                                <span className="text-[10px] text-slate-400 block">Policy</span>
                                <span className="font-bold text-indigo-600 truncate block px-1">{channel.policy?.name || 'Default'}</span>
                            </div>
                        </div>

                        <button className="w-full py-2 rounded-xl bg-white border border-slate-100 text-[10px] font-black text-slate-500 hover:bg-red-50 hover:text-red-500 hover:border-red-100 transition-all">
                            TERMINATE CHANNEL
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SCPChannels;
