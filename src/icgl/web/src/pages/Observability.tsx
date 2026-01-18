import { useState, useEffect } from 'react';
import './Observability.css';
import { Network, Search, Clock, AlertCircle, FileCode } from 'lucide-react';

interface Trace {
    id: string;
    path: string;
    status: 'error' | 'success';
    duration: string;
    timestamp: string;
}

export const Observability = () => {
    const [traces, setTraces] = useState<Trace[]>([]);
    const [selectedTrace, setSelectedTrace] = useState<Trace | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Mock Data
        setTimeout(() => {
            setTraces([
                { id: 'TRC-1024', path: '/api/v1/decision/validate', status: 'success', duration: '120ms', timestamp: '10:42:05' },
                { id: 'TRC-1025', path: '/api/v1/agent/lifecycle', status: 'error', duration: '450ms', timestamp: '10:42:10' },
                { id: 'TRC-1026', path: '/api/v1/memory/retrieve', status: 'success', duration: '85ms', timestamp: '10:42:15' },
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const handleSelectTrace = (trace: Trace) => {
        setSelectedTrace(trace);
    };

    return (
        <div className="observability-page h-full flex overflow-hidden bg-white">
            {/* Sidebar List */}
            <div className="w-1/3 min-w-[300px] border-l border-gray-200 flex flex-col bg-gray-50">
                <div className="p-4 border-b border-gray-200 bg-white">
                    <h2 className="flex items-center gap-2 font-bold text-lg text-gray-800 mb-3">
                        <Network size={18} className="text-blue-600" />
                        سجلات التتبع
                    </h2>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="بحث في السجلات..."
                            className="w-full pl-3 pr-9 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                        />
                        <Search size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                    {loading ? (
                        <div className="text-center p-8 text-gray-400">جاري التحميل...</div>
                    ) : traces.map(trace => (
                        <div
                            key={trace.id}
                            onClick={() => handleSelectTrace(trace)}
                            className={`p-3 rounded-xl cursor-pointer border transition-all hover:shadow-md ${selectedTrace?.id === trace.id
                                    ? 'bg-white border-blue-500 shadow-md ring-1 ring-blue-500/20'
                                    : 'bg-white border-gray-200 hover:border-blue-300'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-1">
                                <span className="font-mono text-xs font-bold text-gray-500">{trace.id}</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${trace.status === 'success' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'
                                    }`}>
                                    {trace.status}
                                </span>
                            </div>
                            <div className="font-semibold text-gray-800 text-sm mb-1 truncate" dir="ltr">{trace.path}</div>
                            <div className="flex items-center gap-3 text-xs text-gray-400">
                                <span className="flex items-center gap-1"><Clock size={10} /> {trace.timestamp}</span>
                                <span>{trace.duration}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-8 overflow-y-auto bg-white relative">
                {selectedTrace ? (
                    <div className="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 mb-1" dir="ltr">{selectedTrace.path}</h1>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <span className="font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-700">{selectedTrace.id}</span>
                                    <span>•</span>
                                    <span>{selectedTrace.timestamp}</span>
                                </div>
                            </div>
                            <div className={`px-4 py-2 rounded-lg font-bold uppercase tracking-wider text-sm flex items-center gap-2 ${selectedTrace.status === 'success' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                                }`}>
                                {selectedTrace.status === 'success' ? <FileCode size={16} /> : <AlertCircle size={16} />}
                                {selectedTrace.status}
                            </div>
                        </div>

                        {/* Timeline Visualization (Mock) */}
                        <div className="space-y-4">
                            <div className="font-bold text-gray-800 mb-4">Timings</div>
                            <div className="relative">
                                <div className="absolute left-0 top-0 bottom-0 w-px bg-gray-200"></div>
                                <div className="space-y-6 pl-6">
                                    <div className="relative">
                                        <div className="absolute -left-[29px] top-1 w-3 h-3 rounded-full bg-blue-500 border-2 border-white shadow-sm"></div>
                                        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                                            <div className="flex justify-between text-sm font-semibold text-gray-800">
                                                <span>Request Received</span>
                                                <span>0ms</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="relative">
                                        <div className="absolute -left-[29px] top-1 w-3 h-3 rounded-full bg-blue-500 border-2 border-white shadow-sm"></div>
                                        <div className="pl-8">
                                            <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 w-3/4">
                                                <div className="flex justify-between text-sm font-semibold text-blue-900">
                                                    <span>Processing</span>
                                                    <span>{parseInt(selectedTrace.duration) * 0.8}ms</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="relative">
                                        <div className="absolute -left-[29px] top-1 w-3 h-3 rounded-full bg-emerald-500 border-2 border-white shadow-sm"></div>
                                        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                                            <div className="flex justify-between text-sm font-semibold text-gray-800">
                                                <span>Response Sent</span>
                                                <span>{selectedTrace.duration}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-300">
                        <Search size={64} className="mb-4 opacity-50" />
                        <p className="text-lg font-medium">اختر سجلاً لعرض التفاصيل</p>
                    </div>
                )}
            </div>
        </div>
    );
};
