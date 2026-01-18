import { useState, useEffect } from 'react';
import './SovereignArchive.css';
import {
    Archive,
    FileText,
    Search,
    Shield,
    FileCheck,
    Eye,
    MessageSquare,
    History,
    Clock,
    CheckCircle,
    AlertCircle,
    FileEdit,
    X
} from 'lucide-react';

interface PlanData {
    status: string;
    consultant_plan?: {
        critique: string;
        missing_policies?: string[];
    };
    drafts?: string[];
}

interface ArchiveItem {
    id: string;
    type: 'decision' | 'policy' | 'report' | 'draft';
    title: string;
    date: string;
    status: 'active' | 'archived' | 'pending' | 'draft';
    tags: string[];
}

interface AuditLog {
    policy_code: string;
    prompt: string;
    response: string;
    timestamp: string;
}

export const SovereignArchive = () => {
    const [policies, setPolicies] = useState<string[]>([]);
    const [drafts, setDrafts] = useState<string[]>([]);
    const [auditState, setAuditState] = useState<PlanData | null>(null);
    const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');
    const [showLogs, setShowLogs] = useState(false);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [policiesRes, draftsRes, planRes, logsRes] = await Promise.all([
                fetch('/archivist/policies'),
                fetch('/archivist/drafts'),
                fetch('/archivist/plan'),
                fetch('/archivist/audit/details')
            ]);

            if (policiesRes.ok) {
                const data = await policiesRes.json();
                setPolicies(data.policies || []);
            }
            if (draftsRes.ok) {
                const data = await draftsRes.json();
                setDrafts(data.drafts || []);
            }
            if (planRes.ok) {
                const data = await planRes.json();
                setAuditState(data);
            }
            if (logsRes.ok) {
                const data = await logsRes.json();
                setAuditLogs(data.logs || []);
            }
        } catch (e) {
            console.error("Fetch failed", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s for live updates
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    const handleAction = async (action: string) => {
        try {
            let res;
            if (action === 'RATIFY') {
                res = await fetch('/archivist/ratify', { method: 'POST', body: JSON.stringify({}) });
            } else if (action === 'APPROVE' || action === 'REJECT') {
                res = await fetch('/archivist/plan/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action })
                });
            }

            if (res && res.ok) {
                setToast({ message: `تم تنفيذ العملية: ${action}`, type: 'success' });
                fetchData();
            }
        } catch {
            setToast({ message: "فشل تنفيذ العملية", type: 'error' });
        }
    };

    // Derived items for the grid
    const allItems: ArchiveItem[] = [
        ...policies.map((p, idx) => ({
            id: `P-${idx}`,
            type: 'policy' as const,
            title: p,
            date: 'Live',
            status: 'active' as const,
            tags: ['official', 'enforced']
        })),
        ...drafts.map((d, idx) => ({
            id: `D-${idx}`,
            type: 'draft' as const,
            title: d,
            date: 'Pending',
            status: 'draft' as const,
            tags: ['review', 'ratification']
        }))
    ];

    const filteredItems = allItems.filter(item => {
        const matchesFilter = filter === 'all' || item.type === filter;
        const matchesSearch = item.title.toLowerCase().includes(search.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const getWorkflowStep = () => {
        if (!auditState || Object.keys(auditState).length === 0) return 0; // IDLE
        if (auditState.status === 'PLAN_GENERATED' || auditState.status === 'PLAN_READY') return 1;
        if (auditState.status === 'DRAFTS_READY') return 2;
        return 0;
    };

    const currentStep = getWorkflowStep();

    return (
        <section className="h-full bg-[#F8FAFC] flex flex-col p-8 animate-in fade-in duration-500 relative overflow-y-auto" aria-label="أرشيف الوثائق">
            {/* 1. Sovereignty Header */}
            <header className="flex items-center justify-between mb-10">
                <div>
                    <h1 className="text-3xl font-extralight text-gray-900 flex items-center gap-4">
                        <div className="p-3 bg-blue-600 rounded-2xl shadow-lg shadow-blue-200">
                            <Archive className="text-white" size={28} />
                        </div>
                        مركز حوكمة الأرشيف
                    </h1>
                    <p className="text-gray-400 mt-2 font-medium tracking-wide">COMMAND & CONTROL • CENTRAL ARCHIVE</p>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={() => setShowLogs(!showLogs)}
                        className="flex items-center gap-2 px-5 py-2.5 bg-white border border-gray-200 text-gray-600 rounded-xl text-sm font-bold hover:bg-gray-50 transition-all shadow-sm"
                    >
                        <History size={18} />
                        سجل التفاعلات
                    </button>
                    <button className="px-6 py-2.5 bg-gray-900 text-white rounded-xl text-sm font-bold shadow-xl shadow-gray-200 hover:bg-black transition-all hover:-translate-y-0.5">
                        تحميل المستندات
                    </button>
                </div>
            </header>

            {/* 2. Governance Workflow Stepper */}
            <div className="mb-12 bg-white rounded-[2rem] p-8 border border-gray-100 shadow-sm">
                <div className="flex items-center justify-between mb-8 px-4">
                    <h2 className="text-sm font-bold text-gray-400 uppercase tracking-widest">مسار الحوكمة الحي (Live Governance Pipeline)</h2>
                    <span className="flex items-center gap-2 text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100 animate-pulse">
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        نظام الحوكمة نشط
                    </span>
                </div>

                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8 relative px-4">
                    {/* Progress Line */}
                    <div className="hidden md:block absolute top-[22px] left-0 w-full h-0.5 bg-gray-100 -z-10">
                        <div
                            className="h-full bg-blue-500 transition-all duration-1000"
                            style={{ width: `${(currentStep / 3.0) * 100}%` }}
                        ></div>
                    </div>

                    {[
                        { icon: Search, label: 'التدقيق', desc: 'مسح الملفات', step: 1 },
                        { icon: MessageSquare, label: 'الاستشارة', desc: 'تحليل AI', step: 1 },
                        { icon: FileText, label: 'المسودات', desc: 'صياغة السياسة', step: 2 },
                        { icon: Shield, label: 'الاعتماد', desc: 'نشر رسمي', step: 3 }
                    ].map((s, i) => {
                        const isCompleted = currentStep > i;
                        const isActive = currentStep === i;
                        return (
                            <div key={i} className={`flex flex-col items-center gap-3 transition-opacity duration-500 ${!isCompleted && !isActive ? 'opacity-40' : 'opacity-100'}`}>
                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 ${isCompleted ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-200' :
                                    isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-200 scale-110' :
                                        'bg-white border border-gray-200 text-gray-400'
                                    }`}>
                                    {isCompleted ? <CheckCircle size={24} /> : <s.icon size={22} />}
                                </div>
                                <div className="text-center">
                                    <p className={`text-sm font-bold ${isActive ? 'text-blue-700' : 'text-gray-900'}`}>{s.label}</p>
                                    <p className="text-[10px] text-gray-400 font-medium">{s.desc}</p>
                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* Granular Context & Sovereignty UI */}
                <div className="mt-10 pt-10 border-t border-gray-50">
                    {currentStep === 1 && auditState?.consultant_plan && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in slide-in-from-bottom-4 duration-700">
                            <div className="bg-blue-50/50 rounded-2xl p-6 border border-blue-100/50">
                                <h3 className="text-sm font-bold text-blue-700 mb-4 flex items-center gap-2">
                                    <AlertCircle size={18} /> ملاحظات المستشار الذكي
                                </h3>
                                <p className="text-gray-700 text-sm leading-relaxed font-medium">
                                    {auditState.consultant_plan.critique}
                                </p>
                                <div className="mt-4 flex flex-wrap gap-2">
                                    {auditState.consultant_plan.missing_policies?.map((p: string) => (
                                        <span key={p} className="px-3 py-1 bg-white text-blue-600 text-[10px] font-bold rounded-lg border border-blue-100">
                                            {p}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div className="flex flex-col justify-center gap-4">
                                <h4 className="text-sm font-bold text-gray-900">القرار السيادي المطلوب:</h4>
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => handleAction('APPROVE')}
                                        className="flex-1 py-4 bg-blue-600 text-white rounded-2xl font-bold text-sm shadow-xl shadow-blue-100 hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
                                    >
                                        <FileEdit size={18} /> صياغة المسودات الآن
                                    </button>
                                    <button
                                        onClick={() => handleAction('REJECT')}
                                        className="px-6 py-4 bg-white border border-gray-200 text-gray-500 rounded-2xl font-bold text-sm hover:bg-red-50 hover:text-red-600 transition-all"
                                    >
                                        تجاهل الخطة
                                    </button>
                                </div>
                                <p className="text-[10px] text-gray-400 text-center italic">بالضغط على صياغة، سيبدأ الأرشيفست باستشارة المستشار لكل سياسة على حدة.</p>
                            </div>
                        </div>
                    )}

                    {currentStep === 2 && (
                        <div className="bg-amber-50/50 rounded-2xl p-8 border border-amber-100/50 animate-in zoom-in-95 duration-500">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2">
                                        <Clock className="animate-pulse" size={20} /> مسودات برسم الاعتماد
                                    </h3>
                                    <p className="text-sm text-amber-700/70 mt-1">تم تجهيز المحتوى الذكي بناءً على تحليل النظام.</p>
                                </div>
                                <button
                                    onClick={() => handleAction('RATIFY')}
                                    className="px-8 py-3 bg-white text-emerald-600 border-2 border-emerald-100 rounded-xl font-bold text-sm shadow-sm hover:bg-emerald-600 hover:text-white transition-all transform hover:scale-105"
                                >
                                    🏛️ اعتماد ونشر كافة السياسات
                                </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                {drafts.map(d => (
                                    <div key={d} className="bg-white p-4 rounded-xl border border-amber-200 flex items-center justify-between group">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg group-hover:bg-amber-100 transition-colors">
                                                <FileText size={18} />
                                            </div>
                                            <span className="text-sm font-bold text-gray-800">{d}</span>
                                        </div>
                                        <button className="text-gray-400 hover:text-gray-900" title="مراجعة المحتوى">
                                            <Eye size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {currentStep === 0 && (
                        <div className="text-center py-6">
                            <p className="text-gray-400 text-sm italic">لا توجد عمليات تدقيق جارية حالياً. يمكنك طلب تدقيق جديد من المكتب الرئيسي.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* 3. Central Archive Grid */}
            <div className="flex-1 overflow-y-auto space-y-6">
                {/* Search & Tabs */}
                <div className="flex items-center gap-4 bg-white p-3 rounded-2xl border border-gray-100 shadow-sm sticky top-0 z-20">
                    <div className="relative flex-1">
                        <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                        <input
                            type="text"
                            placeholder="ابحث في السياسات والقرارات التاريخية..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pr-12 pl-4 py-3 bg-gray-50/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/10 transition-all text-sm font-medium"
                        />
                    </div>
                    <div className="flex items-center gap-2 px-2">
                        {['all', 'policy', 'draft'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-2 rounded-xl text-xs font-bold capitalize transition-all ${filter === f ? 'bg-gray-900 text-white shadow-lg' : 'text-gray-400 hover:bg-gray-50'
                                    }`}
                            >
                                {f === 'all' ? 'الكل' : f === 'policy' ? 'السياسات' : 'المسودات'}
                            </button>
                        ))}
                    </div>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
                        {[1, 2, 3].map(i => <div key={i} className="h-48 bg-gray-100 rounded-[2rem]"></div>)}
                    </div>
                ) : filteredItems.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 bg-white rounded-[2rem] border-2 border-dashed border-gray-100">
                        <Archive size={64} className="text-gray-100 mb-4" />
                        <p className="text-gray-400 font-medium">الأرشيف فارغ حالياً</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-8">
                        {filteredItems.map((item, i) => (
                            <div
                                key={i}
                                className="group relative bg-white border border-gray-100 rounded-[2rem] p-6 shadow-sm hover:shadow-xl hover:shadow-blue-500/5 transition-all duration-500 hover:-translate-y-1 overflow-hidden"
                            >
                                <div className="absolute top-0 left-0 w-2 h-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>

                                <div className="flex justify-between items-start mb-6">
                                    <div className={`p-3 rounded-2xl ${item.status === 'active' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'
                                        }`}>
                                        {item.status === 'active' ? <FileCheck size={24} /> : <Clock size={24} />}
                                    </div>
                                    <span className={`text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest ${item.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                                        }`}>
                                        {item.status}
                                    </span>
                                </div>

                                <h3 className="text-lg font-bold text-gray-900 mb-2 leading-tight group-hover:text-blue-600 transition-colors">
                                    {item.title}
                                </h3>
                                <p className="text-xs text-gray-400 font-mono mb-6">{item.date}</p>

                                <div className="flex flex-wrap gap-2">
                                    {item.tags.map(tag => (
                                        <span key={tag} className="px-3 py-1 bg-gray-50 text-gray-400 text-[9px] font-bold rounded-lg border border-gray-100 group-hover:border-blue-100 group-hover:text-blue-400 transition-colors">
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* 4. Transparency Modal (Interaction Logs) */}
            {showLogs && (
                <div className="fixed inset-0 z-[110] flex items-center justify-center p-6 bg-gray-900/40 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="bg-white w-full max-w-4xl max-h-[85vh] rounded-[3rem] shadow-2xl overflow-hidden flex flex-col border border-gray-100 animate-in zoom-in-95 duration-300">
                        <header className="p-10 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">سجل التفاعلات الشفاف</h1>
                                <p className="text-sm text-gray-400 mt-1 font-mono uppercase tracking-widest">Raw Agent Communication Log</p>
                            </div>
                            <button
                                onClick={() => setShowLogs(false)}
                                className="w-12 h-12 flex items-center justify-center rounded-2xl bg-white border border-gray-100 text-gray-400 hover:text-red-500 transition-all shadow-sm"
                                title="إغلاق السجل"
                                aria-label="إغلاق السجل"
                            >
                                <X size={24} />
                            </button>
                        </header>

                        <div className="flex-1 overflow-y-auto p-10 space-y-10 custom-scrollbar">
                            {auditLogs.length === 0 ? (
                                <div className="text-center py-20 text-gray-400 italic">لا توجد سجلات حوار حالياً. السجل يمتلئ أثناء توليد المسودات.</div>
                            ) : (
                                auditLogs.map((log, i) => (
                                    <div key={i} className="space-y-6">
                                        <div className="flex items-center gap-4">
                                            <span className="px-4 py-1 bg-blue-600 text-white text-xs font-bold rounded-full">{log.policy_code}</span>
                                            <span className="text-xs text-gray-400 font-mono">{log.timestamp}</span>
                                        </div>

                                        {/* Prompt Card */}
                                        <div className="relative pl-8 border-l-2 border-blue-200">
                                            <div className="absolute top-0 -left-1.5 w-3 h-3 bg-blue-200 rounded-full"></div>
                                            <h4 className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-3">Sovereign Command (Prompt)</h4>
                                            <div className="bg-blue-50/30 p-6 rounded-2xl text-xs text-gray-600 font-mono whitespace-pre-wrap leading-relaxed border border-blue-50">
                                                {log.prompt}
                                            </div>
                                        </div>

                                        {/* Response Card */}
                                        <div className="relative pl-8 border-l-2 border-emerald-200">
                                            <div className="absolute top-0 -left-1.5 w-3 h-3 bg-emerald-200 rounded-full"></div>
                                            <h4 className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest mb-3">AI Consultant Output (Response)</h4>
                                            <div className="bg-emerald-50/30 p-6 rounded-2xl text-xs text-gray-700 font-mono whitespace-pre-wrap leading-relaxed border border-emerald-50">
                                                {log.response}
                                            </div>
                                        </div>

                                        {i < auditLogs.length - 1 && <hr className="border-gray-50 mt-12" />}
                                    </div>
                                ))
                            )}
                        </div>

                        <footer className="p-8 bg-gray-50 border-t border-gray-100 text-center">
                            <p className="text-[10px] text-gray-400">جميع هذه الحوارات مسجلة ومشفرة ضمن سجل الحوكمة المركزي.</p>
                        </footer>
                    </div>
                    {/* Backdrop click to close */}
                    <div className="absolute inset-0 -z-10" onClick={() => setShowLogs(false)}></div>
                </div>
            )}

            {/* Zen Toast Notification */}
            {toast && (
                <div className={`fixed bottom-10 left-10 z-[200] px-8 py-5 rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.12)] flex items-center gap-4 animate-in slide-in-from-bottom-6 duration-500 bg-white border border-gray-50`} role="status">
                    <span className="text-2xl">
                        {toast.type === 'success' ? '✨' : toast.type === 'error' ? '⚠️' : 'ℹ️'}
                    </span>
                    <span className="font-medium text-gray-800">{toast.message}</span>
                </div>
            )}
        </section>
    );
};
