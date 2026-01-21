import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, Cog, GitBranch, Play, Workflow } from 'lucide-react';
import { fetchSystemHealth } from '../api/queries';
import { SovereignTerminal } from '../components/terminal/SovereignTerminal';
import { fallbackHealth } from '../data/fallbacks';

export default function OperationsPage() {
    const { data: healthData } = useQuery({
        queryKey: ['system-health'],
        queryFn: fetchSystemHealth,
        staleTime: 30_000,
        initialData: fallbackHealth,
    });

    return (
        <div className="space-y-6">
            <header className="glass rounded-3xl p-6 sm:p-8">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-brand-soft rounded-2xl">
                        <Cog className="w-8 h-8 text-brand-base" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-extrabold text-ink leading-tight">
                            مركز العمليات <span className="text-brand-base">· Operations</span>
                        </h1>
                        <p className="text-sm text-slate-600 mt-1">إدارة سير العمل، مراقبة الأدوات، والتحكم في التنفيذ المباشر (GitOps).</p>
                    </div>
                </div>
            </header>

            <section className="grid lg:grid-cols-2 gap-6">
                <div className="glass rounded-3xl p-1 overflow-hidden h-[600px] border border-slate-200">
                    <SovereignTerminal />
                </div>

                <div className="space-y-6">
                    <div className="glass rounded-3xl p-6 space-y-4">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <Workflow className="w-5 h-5 text-brand-base" />
                            سير العمل النشط
                        </h3>
                        <div className="space-y-3">
                            <WorkflowItem
                                title="GitOps Deployment"
                                status="Executing"
                                progress={65}
                                icon={<GitBranch className="w-4 h-4" />}
                            />
                            <WorkflowItem
                                title="Pattern Matching Engine"
                                status="Idle"
                                progress={0}
                                icon={<Play className="w-4 h-4" />}
                            />
                            <WorkflowItem
                                title="ADR Synchronization"
                                status="Completed"
                                progress={100}
                                icon={<CheckCircle2 className="w-4 h-4" />}
                            />
                        </div>
                    </div>

                    <div className="glass rounded-3xl p-6 space-y-4">
                        <h3 className="font-semibold text-ink">إحصائيات التشغيل</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 rounded-2xl bg-white border border-slate-100">
                                <p className="text-[10px] text-slate-500 font-bold uppercase">Active Workflows</p>
                                <p className="text-2xl font-black text-ink">{healthData?.active_operations ?? 0}</p>
                            </div>
                            <div className="p-4 rounded-2xl bg-white border border-slate-100">
                                <p className="text-[10px] text-slate-500 font-bold uppercase">CPU Usage</p>
                                <p className="text-2xl font-black text-emerald-600">12%</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

function WorkflowItem({ title, status, progress, icon }: { title: string; status: string; progress: number; icon: React.ReactNode }) {
    return (
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">{icon}</div>
                    <div>
                        <p className="text-sm font-bold text-ink">{title}</p>
                        <p className="text-[10px] text-slate-500">{status}</p>
                    </div>
                </div>
                <span className="text-xs font-mono font-bold text-brand-base">{progress}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                    className="h-full bg-brand-base transition-all duration-500"
                    style={{ width: `${progress}%` }}
                />
            </div>
        </div>
    );
}
