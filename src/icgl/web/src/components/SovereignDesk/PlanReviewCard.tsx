import { useState, useEffect } from 'react';

interface ConsultantPlan {
    critique?: string;
    score?: number;
    missing_policies?: string[];
    raw_analysis?: string;
}

// ... unchanged interface PlanData ...



interface PlanData {
    status: string;
    next_step?: string;
    consultant_plan?: ConsultantPlan;
    drafts?: string[];
}

interface PlanReviewCardProps {
    onAuditStateChange?: (auditing: boolean) => void;
}

const PlanReviewCard = ({ onAuditStateChange }: PlanReviewCardProps) => {
    const [plan, setPlan] = useState<PlanData | null>(null);
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState("");

    const fetchPlan = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/archivist/plan");
            const data = await res.json();
            if (data && data.status === "PLAN_READY") {
                setPlan(data);
                // Stop global auditing animation when plan found
                onAuditStateChange?.(false);
            } else {
                setPlan(null);
            }
        } catch (e) {
            console.error("Failed to fetch plan", e);
        }
    };

    useEffect(() => {
        fetchPlan();
        // Poll every 5 seconds to check for new plans
        const interval = setInterval(fetchPlan, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleAction = async (action: string) => {
        setLoading(true);
        // If generating, start global animation
        if (action === 'GENERATE') {
            onAuditStateChange?.(true);
        }

        try {
            let url = "http://127.0.0.1:8000/archivist/plan/action";
            let body: any = { action: action };

            // If we are generating, hit the generation endpoint
            if (action === 'GENERATE') {
                url = "http://127.0.0.1:8000/archivist/plan-improvements";
                body = {};
            } else if (action === 'RATIFY') {
                url = "http://127.0.0.1:8000/archivist/ratify";
                body = { action: 'RATIFY' };
            }

            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            const result = await res.json();
            setMsg(result.message || result.status || result.summary);

            if (action === 'REJECT') {
                setPlan(null);
            } else if (action === 'GENERATE') {
                // After generating, fetch the plan immediately
                await fetchPlan();
            } else if (action === 'APPROVE') {
                // Now moves to DRAFTS_READY, so we fetch plan again
                await fetchPlan();
            } else if (action === 'RATIFY') {
                // Final completion
                setPlan(null);
                setMsg("Policies Ratified Successfully!");
            }

        } catch (e) {
            setMsg("Error executing action");
        }
        setLoading(false);
    };

    // If no plan is pending, show the "Request Audit" state
    if (!plan && !loading) {
        return (
            <div className="bg-white border border-gray-100 rounded-[2rem] p-6 mb-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                    <svg className="w-24 h-24" fill="black" viewBox="0 0 24 24"><path d="M9 11.75c-.69 0-1.25.56-1.25 1.25s.56 1.25 1.25 1.25 1.25-.56 1.25-1.25-.56-1.25-1.25-1.25zm6 0c-.69 0-1.25.56-1.25 1.25s.56 1.25 1.25 1.25 1.25-.56 1.25-1.25-.56-1.25-1.25-1.25zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.29.02-.58.05-.86 2.36-1.05 4.23-2.98 5.21-5.37C11.07 8.33 14.05 10 17.42 10c.78 0 1.53-.09 2.25-.26.21 1.71.33 3.47.33 5.26 0 4.41-3.59 8-8 8z" /></svg>
                </div>

                <h3 className="text-gray-500 text-xs font-bold uppercase tracking-widest mb-1">Audit Status</h3>
                <div className="text-xl font-light text-gray-800 mb-4">
                    System <span className="font-bold text-green-600">Idle</span>
                </div>

                <div className="relative z-10">
                    <p className="text-sm text-gray-400 mb-4">No pending governance plans. System is monitoring.</p>

                    <button
                        onClick={() => handleAction('GENERATE')}
                        className="w-full bg-gray-900 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-black transition-all hover:scale-[1.02]"
                    >
                        <span>🔍</span> Request Deep Audit
                    </button>
                </div>

                {loading && (
                    <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-20">
                        <div className="flex flex-col items-center">
                            <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-2"></div>
                            <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">Auditing...</span>
                        </div>
                    </div>
                )}
            </div>
        )
    }

    if (!plan && loading) return (
        <div className="bg-white border border-gray-100 rounded-[2rem] p-6 mb-6 shadow-sm flex items-center justify-center h-48">
            <div className="flex flex-col items-center animate-pulse">
                <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mb-3">
                    <span className="animate-spin text-xl">⚙️</span>
                </div>
                <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Generating Plan...</span>
            </div>
        </div>
    );

    return (
        <div className="bg-slate-800 border-l-4 border-indigo-500 rounded-lg p-6 mb-6 shadow-xl animate-fade-in relative overflow-hidden">
            {/* Same Existing Active Plan UI ... */}
            <div className="absolute top-0 right-0 p-4 opacity-10">
                <svg className="w-24 h-24" fill="white" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z" /></svg>
            </div>

            <div className="relative z-10">
                <h3 className="text-xl font-bold text-white mb-2 flex items-center">
                    <span className="text-2xl mr-2">🗳️</span>
                    Pending Governance Plan
                </h3>

                {/* DRAFT REVIEW STATE */}
                {plan?.status === 'DRAFTS_READY' ? (
                    <div className="bg-amber-900/40 rounded p-4 mb-4 border border-amber-700">
                        <h4 className="text-amber-300 font-bold mb-2 flex items-center gap-2">
                            <span>📜</span> Drafts Prepared for Ratification
                        </h4>
                        <p className="text-slate-300 text-sm mb-3">
                            The following draft policies have been generated. Review them before final ratification (Publishing to live system).
                        </p>

                        <div className="bg-black/40 rounded p-3 text-xs font-mono text-green-400 mb-4 max-h-40 overflow-y-auto">
                            {plan.drafts && plan.drafts.length > 0 ? (
                                plan.drafts.map((draft, i) => (
                                    <div key={i} className="mb-1">
                                        📄 docs/policies/drafts/{draft}.md <span className="text-slate-500">[NEW]</span>
                                    </div>
                                ))
                            ) : (
                                <div className="text-slate-500">No drafts returned (Check logs).</div>
                            )}
                        </div>

                        <div className="flex gap-4">
                            <button
                                onClick={() => handleAction('RATIFY')}
                                disabled={loading}
                                className="flex-1 bg-amber-600 hover:bg-amber-700 text-white py-2 px-4 rounded font-bold transition-colors flex items-center justify-center gap-2"
                            >
                                {loading ? "Ratifying..." : "🖋️ Ratify & Publish"}
                            </button>

                            <button
                                onClick={() => handleAction('REJECT')}
                                disabled={loading}
                                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-2 px-4 rounded font-bold transition-colors flex items-center justify-center gap-2"
                            >
                                🗑️ Discard
                            </button>
                        </div>
                    </div>
                ) : (
                    // NORMAL PLAN REVIEW STATE
                    <>
                        <div className="bg-slate-900/50 rounded p-4 mb-4 text-slate-300 font-mono text-sm border border-slate-700">
                            {/* Extract critiques or missing items if available, else standard message */}
                            {plan?.consultant_plan && (
                                <div>
                                    <strong className="text-indigo-400">Consultant Critique:</strong>
                                    <p className="mt-1 mb-2 italic">"{plan.consultant_plan.critique || "Review completed."}"</p>

                                    {plan.consultant_plan.raw_analysis && (
                                        <div className="mt-2 mb-2 p-3 bg-black/50 border border-indigo-900/50 rounded-lg text-slate-400 font-mono text-xs whitespace-pre-wrap max-h-80 overflow-y-auto">
                                            <strong className="block text-indigo-300 mb-1 border-b border-indigo-900/30 pb-1">Full Analysis (Raw):</strong>
                                            {plan.consultant_plan.raw_analysis}
                                        </div>
                                    )}

                                    <div className="flex gap-4 mt-2">
                                        <span className="text-xs bg-slate-700 px-2 py-1 rounded">Score: {plan.consultant_plan.score || "N/A"} / 100</span>
                                        <span className="text-xs bg-slate-700 px-2 py-1 rounded">Engine: GPT-4o</span>
                                    </div>
                                </div>
                            )}

                            <div className="mt-3">
                                <strong className="text-green-400">Proposed Actions:</strong>
                                <ul className="list-disc list-inside mt-1 text-slate-400">
                                    <li>Create missing policies based on missing_policies list</li>
                                    <li>Refactor document structure</li>
                                    <li>Log decision in immutable ledger</li>
                                </ul>
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <button
                                onClick={() => handleAction('APPROVE')}
                                disabled={loading}
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded font-bold transition-colors flex items-center justify-center gap-2"
                            >
                                {loading ? "Processing..." : "✅ Approve (Draft)"}
                            </button>

                            <button
                                onClick={() => handleAction('REJECT')}
                                disabled={loading}
                                className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded font-bold transition-colors flex items-center justify-center gap-2"
                            >
                                {loading ? "Processing..." : "❌ Reject Plan"}
                            </button>
                        </div>
                    </>
                )}

                {msg && <div className="mt-3 text-center text-sm text-yellow-400 font-medium">{msg}</div>}
            </div>
        </div>
    );
};

export default PlanReviewCard;
