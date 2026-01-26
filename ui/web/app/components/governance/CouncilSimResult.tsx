import { AlertTriangle, CheckCircle2, Shield, Target } from 'lucide-react';

export interface AgentResult {
    agent_id: string;
    role: string;
    analysis: string;
    recommendations?: string[];
    confidence?: number;
    error?: string;
}

interface CouncilSimResultProps {
    results: AgentResult[];
    topic: string;
}

export function CouncilSimResult({ results, topic }: CouncilSimResultProps) {
    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-indigo-600 p-6 rounded-2xl text-white shadow-lg">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <Shield className="w-6 h-6" /> اجتماع المجلس السيادي: {topic}
                </h3>
                <p className="text-indigo-100 text-sm mt-1 opacity-80">
                    نتائج مداولات {results.length} وكيل تم استدعاؤهم في بيئة محاكاة منظمة.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.map((res, i) => (
                    <div
                        key={i}
                        className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col"
                    >
                        <div className="flex items-center justify-between mb-3">
                            <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-[10px] font-bold uppercase tracking-wider">
                                {res.role}
                            </span>
                            {res.confidence && (
                                <div className="flex items-center gap-1 text-[10px] font-medium text-emerald-600">
                                    <CheckCircle2 className="w-3 h-3" /> {Math.round(res.confidence * 100)}%
                                </div>
                            )}
                        </div>

                        <h4 className="font-bold text-slate-800 text-sm mb-2">{res.agent_id}</h4>

                        <div className="flex-1 overflow-y-auto max-h-32 mb-3 scrollbar-hide">
                            {res.error ? (
                                <p className="text-rose-500 text-xs italic flex items-center gap-1">
                                    <AlertTriangle className="w-3 h-3" /> فشل التحليل: {res.error}
                                </p>
                            ) : (
                                <p className="text-slate-600 text-xs leading-relaxed">
                                    {res.analysis.length > 200 ? res.analysis.substring(0, 200) + '...' : res.analysis}
                                </p>
                            )}
                        </div>

                        {res.recommendations && res.recommendations.length > 0 && (
                            <div className="pt-3 border-t border-slate-100">
                                <p className="text-[10px] font-bold text-slate-400 uppercase mb-1 flex items-center gap-1">
                                    <Target className="w-3 h-3" /> التوصية الأساسية
                                </p>
                                <p className="text-slate-700 text-[11px] font-medium truncate">
                                    {res.recommendations[0]}
                                </p>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
