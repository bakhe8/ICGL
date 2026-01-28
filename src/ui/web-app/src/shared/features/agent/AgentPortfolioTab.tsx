import { useQuery } from '@tanstack/react-query';
import { Activity, BarChart3, CheckCircle2, Clock, Hash, ThumbsUp, XCircle } from 'lucide-react';
import { fetchAgentHistory, fetchAgentStats } from '../../../domains/hall/api';

interface AgentHistoryItem {
    run_id: string;
    title: string;
    timestamp: string;
    role: string;
    summary: string;
    confidence: number;
    verdict: string;
    concerns_count: number;
    tags: string[];
}

interface AgentStats {
    total_runs: number;
    approval_rate: number;
    strictness: number;
    top_keywords: [string, number][];
}

export function AgentPortfolioTab({ agentId }: { agentId: string }) {

    // Fetch History
    const historyQuery = useQuery<{ history: AgentHistoryItem[] }>({
        queryKey: ['agent-history', agentId],
        queryFn: () => fetchAgentHistory(agentId)
    });

    // Fetch Analytics
    const statsQuery = useQuery<AgentStats>({
        queryKey: ['agent-stats', agentId],
        queryFn: () => fetchAgentStats(agentId)
    });

    if (historyQuery.isLoading || statsQuery.isLoading) {
        return <div className="p-8 text-center text-slate-400">Loading Portfolio...</div>;
    }

    const history = historyQuery.data?.history || [];
    const stats = statsQuery.data;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Analytics Cards */}
            <section className="grid sm:grid-cols-3 gap-4">
                <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
                            <Activity className="w-5 h-5" />
                        </div>
                        <div className="text-sm font-bold text-slate-500 uppercase">Work Volume</div>
                    </div>
                    <p className="text-2xl font-black text-slate-900">{stats?.total_runs || 0} <span className="text-sm font-normal text-slate-400">Analysis Runs</span></p>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
                            <ThumbsUp className="w-5 h-5" />
                        </div>
                        <div className="text-sm font-bold text-slate-500 uppercase">Approval Rate</div>
                    </div>
                    <div className="flex items-center gap-2">
                        <p className="text-2xl font-black text-slate-900">{(stats?.approval_rate || 0) * 100}%</p>
                        <div className="h-2 flex-1 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500" style={{ width: `${(stats?.approval_rate || 0) * 100}%` }}></div>
                        </div>
                    </div>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 rounded-lg bg-rose-50 text-rose-600">
                            <BarChart3 className="w-5 h-5" />
                        </div>
                        <div className="text-sm font-bold text-slate-500 uppercase">Strictness Score</div>
                    </div>
                    <p className="text-2xl font-black text-slate-900">{((stats?.strictness || 0) * 100).toFixed(0)} <span className="text-sm font-normal text-slate-400">/ 100</span></p>
                    <p className="text-xs text-slate-400 mt-1">Higher means more critical/skeptical.</p>
                </div>
            </section>

            {/* Expertise Cloud */}
            {stats?.top_keywords && stats.top_keywords.length > 0 && (
                <section className="glass rounded-2xl p-6">
                    <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Hash className="w-4 h-4 text-indigo-500" /> Expertise Cloud (Top Keywords)
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {stats.top_keywords.map(([word, count]) => (
                            <span key={word} className="px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 text-sm font-medium border border-indigo-100 flex items-center gap-2">
                                #{word} <span className="bg-indigo-200 text-indigo-800 text-[10px] px-1.5 rounded-md min-w-[20px] text-center">{count}</span>
                            </span>
                        ))}
                    </div>
                </section>
            )}

            {/* Contribution Timeline */}
            <section className="space-y-4">
                <h3 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                    <Clock className="w-5 h-5 text-indigo-500" /> Recent Contributions
                </h3>

                {history.length === 0 ? (
                    <div className="text-center py-12 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                        <p className="text-slate-400 font-medium">No contribution history found.</p>
                        <p className="text-xs text-slate-400 mt-1">Run some ideas to see this agent in action.</p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {history.map((item) => (
                            <div key={item.run_id} className="p-5 rounded-2xl bg-white border border-slate-100 hover:shadow-md transition-all flex gap-4 group">
                                <div className="mt-1">
                                    {item.verdict === 'APPROVED' ? (
                                        <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
                                            <CheckCircle2 className="w-6 h-6" />
                                        </div>
                                    ) : (
                                        <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600">
                                            <XCircle className="w-6 h-6" />
                                        </div>
                                    )}
                                </div>
                                <div className="flex-1 space-y-2">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h4 className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{item.title}</h4>
                                            <p className="text-xs text-slate-500 font-mono mt-0.5">{new Date(item.timestamp).toLocaleString()} · Role: {item.role}</p>
                                        </div>
                                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${item.verdict === 'APPROVED' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                                            }`}>
                                            {item.verdict}
                                        </span>
                                    </div>

                                    <div className="bg-slate-50 p-3 rounded-xl text-sm text-slate-600 leading-relaxed border border-slate-100">
                                        {item.summary}
                                    </div>

                                    <div className="flex flex-wrap gap-2 text-[10px]">
                                        {item.tags.map(tag => (
                                            <span key={tag} className="px-2 py-0.5 rounded-md bg-white border border-slate-200 text-slate-500 font-mono">
                                                {tag.toUpperCase()}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
}
