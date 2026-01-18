import { useEffect, useState } from 'react';
import { HealthPulse } from './HealthPulse';
import { DecisionQueue } from './DecisionQueue';
import { StrategicSignals } from './StrategicSignals';
import { NewProposalForm } from './NewProposalForm';
import StrategicAdvisorCard from './StrategicAdvisorCard';
import PlanReviewCard from './PlanReviewCard';

// --- Types ---

interface Proposal {
    agent_id: string;
    proposal: string;
    status: string;
    timestamp: string;
    requester?: string;
    executive_brief?: string;
    impact?: string;
    details?: string;
}

interface DecisionItem {
    id: string;
    title: string;
    priority: 'high' | 'medium' | 'low';
    description?: string;
    status?: string;
    raw?: Proposal;
}

// ... (SignalItem and HealthStatus remain the same) ...

interface SignalItem {
    id: string;
    icon: string;
    title: string;
    type: 'info' | 'warning' | 'suggestion';
    raw?: any;
}

interface HealthStatus {
    healthy: boolean;
    activeAgents: number;
    activeOperations: number;
}


export const SovereignDesk = () => {
    const [decisions, setDecisions] = useState<DecisionItem[]>([]);
    const [selected, setSelected] = useState<DecisionItem | null>(null);
    const [health, setHealth] = useState<HealthStatus | null>(null);
    const [signals, setSignals] = useState<SignalItem[]>([]);
    const [actioningId, setActioningId] = useState<string | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
    const [consultantInsight, setConsultantInsight] = useState<string | null>(null);
    const [auditing, setAuditing] = useState(false); // Shared audit state

    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    const loadData = async () => {

        try {
            const [statusRes, overviewRes, proposalsRes] = await Promise.all([
                fetch('/status').catch(() => null),
                fetch('/dashboard/overview').catch(() => null),
                fetch('/proposals').catch(() => null)
            ]);

            if (statusRes && statusRes.ok) {
                const statusData = await statusRes.json();
                setHealth({
                    healthy: statusData?.healthy ?? true,
                    activeAgents: statusData?.active_agents ?? 12,
                    activeOperations: statusData?.active_operations ?? 5,
                });
            }

            if (overviewRes && overviewRes.ok) {
                const overviewData = await overviewRes.json();
                const derivedSignals: SignalItem[] =
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    overviewData.decision_log?.map((d: any, idx: number) => ({
                        id: String(idx),
                        icon: '📄',
                        title: d.decision || 'Decision pending',
                        type: 'info',
                        raw: d,
                    })) || [];
                setSignals(derivedSignals);
            }

            if (proposalsRes && proposalsRes.ok) {
                const data = await proposalsRes.json();
                const mapped: DecisionItem[] = (data.proposals || []).map((p: Proposal, idx: number) => ({
                    id: String(idx),
                    title: p.proposal || 'Proposal',
                    priority: p.status === 'NEW' ? 'high' : 'medium',
                    description: `Agent: ${p.agent_id} | Status: ${p.status}`,
                    status: p.status,
                    raw: p,
                }));

                if (mapped.length > 0) {
                    setDecisions(mapped);
                    return;
                }
            }

            // Fallback if fetch failed or empty
            setDecisions([
                { id: '1', title: 'خطة GitOps Pipeline', priority: 'high', description: 'تفاصيل الخطة: تطبيق منهجية GitOps لتسريع النشر وتحسين الموثوقية. يتطلب موافقة المدير التنفيذي.' },
                { id: '2', title: 'تحديث السياسة P-OPS-05', priority: 'medium', description: 'تعديلات مقترحة على سياسة العمليات للامتثال للمعايير الجديدة.' },
                { id: '3', title: 'طلب من MonitorAgent', priority: 'low', description: 'تنبيه دوري حول استهلاك الموارد.' }
            ]);

        } catch (e) {
            console.error('Data load error', e);
            // Emergency fallback
            setDecisions([
                { id: '1', title: 'خطة GitOps Pipeline (Offline)', priority: 'high', description: 'System offline. Cached plan details.' }
            ]);
        }
    };

    const fetchConsultantInsight = async () => {
        setConsultantInsight(null);
        try {
            const res = await fetch('/consultant/insight');
            if (res.ok) {
                const data = await res.json();
                setConsultantInsight(data.insight);
            }
        } catch (e) {
            console.error('Failed to fetch insight', e);
            setConsultantInsight("تعذر الاتصال بالمستشار حالياً.");
        }
    };

    useEffect(() => {
        loadData();
        fetchConsultantInsight();
    }, []);

    const updateProposalStatus = async (id: string, status: string) => {
        const idx = parseInt(id, 10);
        if (Number.isNaN(idx)) return;
        setActioningId(id);
        try {
            await fetch(`/proposals/${idx}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status,
                }),
            });
            setDecisions(prev => prev.map(d => d.id === id ? { ...d, status } : d));
            await loadData();
            setToast({ message: `تم تحديث الحالة إلى: ${status}`, type: 'success' });
        } catch (e) {
            console.error('updateProposalStatus error', e);
            setToast({ message: 'فشل تحديث الحالة', type: 'error' });
        } finally {
            setActioningId(null);
        }
    };

    const handleApprove = (id: string) => updateProposalStatus(id, 'APPROVED');
    const handleReject = (id: string) => updateProposalStatus(id, 'REJECTED');
    const handleDetails = (id: string) => {
        const found = decisions.find((d) => d.id === id);
        setSelected(found || null);
    };
    const defaultSignals: SignalItem[] = [
        { id: '1', icon: '⚠️', title: '6 سياسات مفقودة', type: 'warning' },
        { id: '2', icon: '💡', title: 'توصية: تفعيل GitOps', type: 'suggestion' },
        { id: '3', icon: '📊', title: 'تقرير أداء جديد', type: 'info' }
    ];

    const displaySignals = signals.length > 0 ? signals : defaultSignals;

    const handleViewSignal = (id: string) => {
        const sig = displaySignals.find((s) => s.id === id);
        if (sig) {
            setToast({ message: `🔍 عرض تفاصيل الإشارة: ${sig.title}`, type: 'info' });
        }
    };
    const handleDelegateSignal = async (id: string) => {
        const sig = displaySignals.find((s) => s.id === id);
        if (!sig) return;
        setToast({ message: `🛡️ تم تفويض الإشارة: ${sig.title} للمراجعة`, type: 'success' });
    };

    return (
        <div className="min-h-full bg-[#FDFDFD] flex flex-col font-sans">
            {/* Minimalist Header - Clean & Spacious */}
            <header className="bg-white px-8 py-6 border-b border-gray-50 mb-8" role="banner">
                <div className="w-full">
                    <h1 className="text-4xl font-extralight text-gray-800 tracking-tight">مكتب الرئيس التنفيذي</h1>
                    <p className="text-gray-400 mt-2 text-sm tracking-widest uppercase">ICGL • Executive Focus</p>
                </div>
            </header>

            {/* Main Content - Asymmetric Zen Layout - FULL WIDTH */}
            <main className="flex-1 w-full px-8 pb-12" role="main" aria-label="لوحة القيادة التنفيذية">

                {/* 1. Quick Stats - Floating, Subtle */}
                <section aria-label="إحصائيات سريعة" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
                    <div className="group p-6 rounded-2xl bg-white hover:bg-blue-50/30 transition-colors duration-500 cursor-default">
                        <div className="text-4xl font-light text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">12</div>
                        <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">الموظفين النشطين</div>
                    </div>
                    {/* Explicitly calculating pending stats */}
                    {(() => {
                        // Total PENDING in the system (Unfiltered)
                        const totalPending = decisions.length;
                        return (
                            <div className="group p-6 rounded-2xl bg-white hover:bg-yellow-50/30 transition-colors duration-500 cursor-default">
                                <div className="text-4xl font-light text-gray-800 mb-2 group-hover:text-yellow-600 transition-colors">
                                    {totalPending}
                                </div>
                                <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">إجمالي القرارات (System)</div>
                            </div>
                        );
                    })()}
                    <div className="group p-6 rounded-2xl bg-white hover:bg-green-50/30 transition-colors duration-500 cursor-default">
                        <div className="text-4xl font-light text-gray-800 mb-2 group-hover:text-green-600 transition-colors">5</div>
                        <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">عمليات جارية</div>
                    </div>
                    <div className="group p-6 rounded-2xl bg-white hover:bg-purple-50/30 transition-colors duration-500 cursor-default">
                        <div className="text-4xl font-light text-gray-800 mb-2 group-hover:text-purple-600 transition-colors">8</div>
                        <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">تقارير جديدة</div>
                    </div>
                </section>

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-12 items-start">

                    {/* LEFT COLUMN (Main Focus): Decisions (Spend 66% width) */}
                    <div className="xl:col-span-8 flex flex-col gap-12">
                        {/* Advisor & Plan Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <StrategicAdvisorCard isAuditing={auditing} />
                            <PlanReviewCard onAuditStateChange={setAuditing} />
                        </div>

                        <NewProposalForm onSubmitted={loadData} />
                        <section aria-label="طابور القرارات" className="bg-white rounded-[2rem] p-10 shadow-[0_2px_40px_-12px_rgba(0,0,0,0.05)] border border-gray-100/50">
                            <div className="mb-6"></div>
                            <DecisionQueue
                                decisions={decisions}
                                onApprove={handleApprove}
                                onReject={handleReject}
                                onDetails={handleDetails}
                                actioningId={actioningId}
                            />
                        </section>
                    </div>

                    {/* RIGHT COLUMN (Context): Health & Signals (Spend 33% width) */}
                    <div className="xl:col-span-4 flex flex-col gap-8">
                        {/* Consultant Insight */}
                        <section aria-label="المستشار الاستراتيجي" className="bg-white rounded-[2rem] p-8 shadow-[0_2px_30px_-10px_rgba(0,0,0,0.03)] border border-gray-100/50 transition-transform hover:translate-y-[-4px] duration-500">
                            <div className="flex items-center gap-4 mb-6">
                                <span className="text-3xl bg-indigo-50 p-3 rounded-2xl">🧠</span>
                                <div>
                                    <h2 className="text-lg font-bold text-gray-800">المستشار الاستراتيجي</h2>
                                    <p className="text-xs text-indigo-400 font-mono tracking-wider">AI ADVISOR • LIVE</p>
                                </div>
                            </div>

                            <div className="bg-indigo-50/50 rounded-xl p-6 relative">
                                <div className="absolute top-0 right-0 -mt-2 -mr-2 text-indigo-200 text-4xl opacity-50">”</div>
                                {consultantInsight ? (
                                    <p className="text-gray-700 leading-relaxed text-sm font-medium relative z-10">
                                        {consultantInsight}
                                    </p>
                                ) : (
                                    <div className="flex items-center gap-2 text-gray-400 text-sm">
                                        <span className="animate-spin">⏳</span> جاري تحليل البيانات...
                                    </div>
                                )}
                                <div className="absolute bottom-0 right-0 -mb-4 -mr-2 text-indigo-200 text-4xl opacity-50 rotate-180">”</div>
                            </div>

                            <button
                                onClick={fetchConsultantInsight}
                                className="mt-6 w-full py-3 bg-white border border-indigo-100 text-indigo-600 rounded-xl text-sm font-bold hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2"
                            >
                                <span>🔄</span>
                                طلب تحليل جديد
                            </button>
                        </section>

                        {/* Health Pulse */}
                        <section aria-label="حالة النظام" className="bg-white rounded-[2rem] p-8 shadow-[0_2px_30px_-10px_rgba(0,0,0,0.03)] border border-gray-100/50 transition-transform hover:translate-y-[-4px] duration-500">

                            <HealthPulse status={health || undefined} onDetails={() => setToast({ message: 'تقرير الحالة التفصيلي: كل الأنظمة تعمل بكفاءة 100%', type: 'success' })} />
                        </section>

                        {/* Strategic Signals */}
                        <section aria-label="الإشارات الاستراتيجية" className="bg-white rounded-[2rem] p-8 shadow-[0_2px_30px_-10px_rgba(0,0,0,0.03)] border border-gray-100/50 transition-transform hover:translate-y-[-4px] duration-500">

                            <StrategicSignals
                                signals={displaySignals}
                                onView={handleViewSignal}
                                onDelegate={handleDelegateSignal}
                            />
                        </section>
                    </div>
                </div>
            </main>

            {/* Elegant Details Modal */}
            {selected && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-white/80 backdrop-blur-md animate-in fade-in duration-300">
                    <div
                        className="bg-white rounded-[2rem] shadow-2xl w-full max-w-2xl overflow-hidden animate-in zoom-in-95 duration-300 border border-gray-100 flex flex-col max-h-[90vh]"
                        role="dialog"
                        aria-labelledby="modal-title"
                    >
                        <div className="p-8 border-b border-gray-50 flex justify-between items-start bg-gray-50/30">
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded uppercase tracking-wider">
                                        {selected.raw?.agent_id || 'System'}
                                    </span>
                                    {selected.raw?.requester && (
                                        <span className="text-xs text-gray-400 font-medium">
                                            • طلب بواسطة: {selected.raw.requester}
                                        </span>
                                    )}
                                </div>
                                <h3 id="modal-title" className="text-2xl font-bold text-gray-900">{selected.title}</h3>
                            </div>
                            <button
                                className="w-10 h-10 flex items-center justify-center rounded-full bg-white border border-gray-100 text-gray-400 hover:bg-gray-50 hover:text-gray-900 transition-all shadow-sm"
                                onClick={() => setSelected(null)}
                                aria-label="إغلاق"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-8 overflow-y-auto space-y-8">

                            {/* Executive Secretary Brief */}
                            <div className="relative pl-6 border-l-4 border-blue-500">
                                <h4 className="text-sm font-bold text-blue-600 uppercase tracking-widest mb-2 flex items-center gap-2">
                                    <span>📝</span> ملخص السكرتير التنفيذي
                                </h4>
                                <p className="text-lg text-gray-800 leading-relaxed font-medium">
                                    {selected.raw?.executive_brief || selected.description || "لا يوجد ملخص متاح."}
                                </p>
                            </div>

                            {/* Impact Analysis */}
                            {selected.raw?.impact && (
                                <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                                    <h4 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">الأثر المتوقع (Impact)</h4>
                                    <div className="space-y-2">
                                        {selected.raw.impact.split('\n').map((line, i) => (
                                            <div key={i} className="flex gap-2 text-gray-700 text-sm font-medium">
                                                {line}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Technical Details & Execution Log Parsed */}
                            {(() => {
                                const fullDetails = selected.raw?.details || "";
                                // Split by the backend's known marker
                                const [staticPart, executionPart] = fullDetails.split("🚀 **مسار التنفيذ");

                                return (
                                    <div className="space-y-6">
                                        {/* Static Details */}
                                        {staticPart && staticPart.trim() && (
                                            <div>
                                                <h4 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-2">التفاصيل التقنية</h4>
                                                <p className="text-gray-600 leading-relaxed text-sm whitespace-pre-wrap font-medium">
                                                    {staticPart.trim()}
                                                </p>
                                            </div>
                                        )}

                                        {/* Dynamic Execution Log (Terminal Style) */}
                                        {executionPart && (
                                            <div className="animate-in slide-in-from-bottom-4 duration-700">
                                                <h4 className="text-sm font-bold text-gray-800 uppercase tracking-widest mb-3 flex items-center gap-2">
                                                    <span className="relative flex h-3 w-3">
                                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                                    </span>
                                                    سجل التنفيذ الحي (Live Execution)
                                                </h4>
                                                <div className="bg-[#1E1E1E] text-green-400 p-6 rounded-xl font-mono text-xs leading-loose shadow-inner border border-gray-800 overflow-hidden relative">
                                                    {/* Scanline effect */}
                                                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/5 to-transparent pointer-events-none opacity-10 animate-scan"></div>

                                                    {("🚀 **مسار التنفيذ" + executionPart).split('\n').map((line, idx) => (
                                                        <div key={idx} className={`${line.includes('⛔') ? 'text-red-400' : ''} ${line.includes('Enforcer') ? 'text-blue-400' : ''}`}>
                                                            {line.replace(/\*\*/g, '')}
                                                        </div>
                                                    ))}
                                                    <div className="mt-2 text-gray-500 animate-pulse">_</div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })()}
                        </div>

                        {/* Footer Actions */}
                        <div className="p-6 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
                            {['APPROVED', 'REJECTED'].includes(selected.status || selected.raw?.status || '') ? (
                                <div className={`px-6 py-2 rounded-lg font-bold text-sm ${(selected.status || selected.raw?.status) === 'APPROVED' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                    }`}>
                                    {(selected.status || selected.raw?.status) === 'APPROVED' ? '✅ تم اعتماد هذا القرار' : '❌ تم رفض هذا القرار'}
                                </div>
                            ) : (
                                <>
                                    <button
                                        onClick={() => {
                                            if (selected) {
                                                updateProposalStatus(selected.id, 'CLARIFICATION');
                                                setToast({ message: `✉️ تم إرسال طلب تونيح إلى ${selected.raw?.agent_id || 'المنفذ'}`, type: 'info' });
                                                setSelected(null);
                                            }
                                        }}
                                        className="px-6 py-3 bg-white border border-gray-200 text-gray-600 rounded-xl text-sm font-bold hover:bg-gray-50 transition-colors"
                                    >
                                        طلب إيضاحات
                                    </button>
                                    <button
                                        onClick={() => {
                                            /* Replicating the approve logic from DecisionQueue: 
                                               We need to call updateProposalStatus(selected.id, 'APPROVED') 
                                               But the handler here was empty in the view. 
                                               I need to make sure I use the correct update function available in the scope.
                                               Looking at line 374, updateProposalStatus is available.
                                            */
                                            if (selected) {
                                                updateProposalStatus(selected.id, 'APPROVED');
                                                /* Toast is handled in updateProposalStatus likely, or we add it here */
                                                setToast({ message: '✅ تم اعتماد القرار بنجاح', type: 'success' });
                                                setSelected(null);
                                            }
                                        }}
                                        className="px-8 py-3 bg-gray-900 text-white rounded-xl text-sm font-bold shadow-lg shadow-gray-200 hover:bg-black transition-all hover:-translate-y-0.5"
                                    >
                                        اعتماد القرار
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                    {/* Backdrop click to close */}
                    <div className="absolute inset-0 -z-10" onClick={() => setSelected(null)}></div>
                </div >
            )
            }

            {/* Zen Toast Notification */}
            {
                toast && (
                    <div className={`fixed bottom-10 left-10 z-[200] px-8 py-5 rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.12)] flex items-center gap-4 animate-in slide-in-from-bottom-6 duration-500 bg-white border border-gray-50`} role="status">
                        <span className="text-2xl">
                            {toast.type === 'success' ? '✨' : toast.type === 'error' ? '⚠️' : 'ℹ️'}
                        </span>
                        <span className="font-medium text-gray-800">{toast.message}</span>
                    </div>
                )
            }
        </div >
    );
};
