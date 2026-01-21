import { Flag, GraduationCap, Map, Milestone, Target } from 'lucide-react';

export default function RoadmapPage() {
    return (
        <div className="space-y-6">
            <header className="glass rounded-3xl p-6 sm:p-8">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-brand-soft rounded-2xl">
                        <GraduationCap className="w-8 h-8 text-brand-base" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-extrabold text-ink leading-tight">
                            خارطة الطريق السيادية <span className="text-brand-base">· Roadmap</span>
                        </h1>
                        <p className="text-sm text-slate-600 mt-1">الرؤية المستقبلية، المعالم القادمة، والأهداف الاستراتيجية لـ ICGL.</p>
                    </div>
                </div>
            </header>

            <section className="glass rounded-3xl p-8 space-y-12">
                <div className="relative">
                    <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-brand-base to-slate-200 rounded-full" />

                    <div className="space-y-12">
                        <RoadmapMilestone
                            icon={<Flag className="w-5 h-5" />}
                            title="Phase 1: Foundation (Completed)"
                            desc="بناء المحرك الأساسي، تحويل الذاكرة إلى LanceDB، وتأسيس لوحة التحكم السيادية."
                            status="DONE"
                        />
                        <RoadmapMilestone
                            icon={<Target className="w-5 h-5" />}
                            title="Phase 2: Advanced Reasoning (In Progress)"
                            desc="تحسين قدرات العملاء على حل التعارضات المعقدة وتوسيع نطاق الربط مع GitOps."
                            status="ACTIVE"
                        />
                        <RoadmapMilestone
                            icon={<Map className="w-5 h-5" />}
                            title="Phase 3: Multi-Org Sovereignty"
                            desc="دعم الحوكمة الموزعة عبر عدة مؤسسات معاً في شبكة موحدة."
                            status="PLANNED"
                        />
                        <RoadmapMilestone
                            icon={<Milestone className="w-5 h-5" />}
                            title="Phase 4: Autonomous Evolution"
                            desc="تمكين النظام من اقتراح تعديلات على سياساته الخاصة بناءً على الأنماط الطويلة الأمد."
                            status="FUTURE"
                        />
                    </div>
                </div>
            </section>
        </div>
    );
}

function RoadmapMilestone({ icon, title, desc, status }: { icon: React.ReactNode; title: string; desc: string; status: 'DONE' | 'ACTIVE' | 'PLANNED' | 'FUTURE' }) {
    const colors = {
        DONE: 'border-emerald-500 bg-emerald-50 text-emerald-700',
        ACTIVE: 'border-brand-base bg-brand-soft text-brand-base shadow-lg shadow-brand-base/20',
        PLANNED: 'border-slate-300 bg-white text-slate-600',
        FUTURE: 'border-slate-200 bg-slate-50 text-slate-400 opacity-60',
    };

    return (
        <div className="relative pl-24 group">
            <div className={`absolute left-0 top-0 w-16 h-16 rounded-2xl border-2 grid place-items-center z-10 transition-all ${colors[status]}`}>
                {icon}
            </div>
            <div>
                <h4 className="text-xl font-bold text-ink mb-2">{title}</h4>
                <p className="text-slate-600 max-w-2xl leading-relaxed">{desc}</p>
                <div className="mt-3 flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter ${colors[status]}`}>
                        {status}
                    </span>
                </div>
            </div>
        </div>
    );
}
