
import { useState } from 'react';
import TraceVisualization from '@web-ui/components/admin/TraceVisualization';

const SCPTraces = () => {
    const [traceId, setTraceId] = useState('');
    const [activeTraceId, setActiveTraceId] = useState<string | null>(null);

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500 overflow-hidden">
            <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-bold text-slate-800">🔍 Real-World Trace Visualizer</h3>
                    <div className="flex gap-2">
                        <input
                            className="bg-slate-100 border-none rounded-xl px-4 py-2 text-xs focus:ring-2 focus:ring-indigo-500/20 outline-none w-64"
                            placeholder="Enter Trace ID (e.g., trace_...)"
                            value={traceId}
                            onChange={e => setTraceId(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && setActiveTraceId(traceId)}
                        />
                        <button
                            onClick={() => setActiveTraceId(traceId)}
                            className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-indigo-200"
                        >
                            LOAD
                        </button>
                    </div>
                </div>
                {!activeTraceId && (
                    <p className="text-[11px] text-slate-500 italic">Enter a low-level trace ID to inspect internal agent state transitions and system calls.</p>
                )}
            </div>

            <div className="flex-1 bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 p-6">
                {activeTraceId ? (
                    <div className="h-full overflow-y-auto pr-2 custom-scrollbar">
                        <TraceVisualization traceId={activeTraceId} />
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-center p-10 opacity-30">
                        <div className="w-12 h-12 rounded-full border border-white/20 flex items-center justify-center mb-4 text-white">📡</div>
                        <span className="text-white text-sm font-medium">Ready for trace input</span>
                    </div>
                )}
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
            `}} />
        </div>
    );
};

export default SCPTraces;
