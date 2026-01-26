
import { useEffect, useState } from 'react';
import TraceVisualization from '../components/admin/TraceVisualization';

interface TraceSummary {
    trace_id: string;
    start_time: string;
    end_time: string;
    event_count: number;
    adr_id: string | null;
    session_id: string | null;
}

const ObservabilityPage = () => {
    const [traces, setTraces] = useState<TraceSummary[]>([]);
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTraces();
    }, []);

    const fetchTraces = async () => {
        try {
            setLoading(true);
            const baseUrl = 'http://127.0.0.1:8000';
            const res = await fetch(`${baseUrl}/observability/traces?limit=50`);
            const data = await res.json();
            setTraces(data.traces || []);
        } catch (err) {
            console.error('Failed to fetch traces:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-[calc(100vh-12rem)] gap-6 animate-in fade-in duration-700">
            {/* Sidebar Traces List */}
            <div className="w-80 bg-white border border-slate-200 rounded-3xl flex flex-col overflow-hidden shadow-sm">
                <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <h2 className="font-bold text-slate-800 flex items-center gap-2">
                        <span>🔍 Traces</span>
                    </h2>
                    <button
                        onClick={fetchTraces}
                        className="p-1.5 hover:bg-slate-200 rounded-lg transition-colors text-slate-400"
                    >
                        ↻
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                    {loading ? (
                        <div className="p-4 text-center text-slate-400 animate-pulse text-xs">Loading execution logs...</div>
                    ) : (
                        traces.map((trace, index) => (
                            <button
                                key={trace.trace_id || index}
                                className={`w-full text-left p-3 rounded-2xl border transition-all ${selectedTraceId === trace.trace_id
                                    ? 'bg-indigo-50 border-indigo-200 shadow-sm'
                                    : 'bg-white border-transparent hover:border-slate-200 hover:bg-slate-50'
                                    }`}
                                onClick={() => setSelectedTraceId(trace.trace_id)}
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-[10px] font-mono text-slate-400">
                                        {trace.start_time ? new Date(trace.start_time).toLocaleTimeString() : '--:--:--'}
                                    </span>
                                    <span className={`px-1.5 py-0.5 rounded-full text-[9px] font-bold ${trace.event_count > 10 ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-500'
                                        }`}>
                                        {trace.event_count} evts
                                    </span>
                                </div>
                                <div className="text-xs font-bold text-slate-700 truncate">{trace.trace_id?.slice(0, 12) || '---'}...</div>
                                {trace.adr_id && (
                                    <div className="text-[9px] text-indigo-500 font-bold mt-1 uppercase tracking-tighter">ADR: {trace.adr_id}</div>
                                )}
                            </button>
                        ))
                    )}
                </div>
            </div>

            {/* Main Trace Visualization */}
            <div className="flex-1 bg-slate-900 rounded-3xl p-8 border border-slate-800 shadow-2xl relative overflow-hidden flex flex-col">
                <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.05),transparent)] pointer-events-none" />

                {selectedTraceId ? (
                    <div className="flex-1 min-h-0 overflow-y-auto pr-2 custom-scrollbar">
                        <TraceVisualization traceId={selectedTraceId} />
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-center">
                        <div className="w-16 h-16 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mb-4 text-slate-500">
                            🔍
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Select a trace to visualize</h3>
                        <p className="text-slate-500 text-sm max-w-xs">View the complete step-by-step reasoning cycle of the extended mind.</p>
                    </div>
                )}
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .custom-scrollbar::-webkit-scrollbar { width: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
            `}} />
        </div>
    );
};

export default ObservabilityPage;
