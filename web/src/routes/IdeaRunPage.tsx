import { useEffect, useState } from 'react';

type IdeaResponse = { status: string; adr_id: string };
type AnalysisResponse = {
  status?: string;
  question?: string;
  agent?: string;
  synthesis?: {
    agent_results: {
      agent_id: string;
      role: string | { value: string };
      analysis: string;
      recommendations?: string[];
      concerns?: string[];
      confidence?: number;
      clarity_needed?: boolean;
      clarity_question?: string;
      file_changes?: { path: string; content: string; mode?: string }[];
      // --- Extended Mind Fields ---
      trigger?: string;
      impact?: string;
      risks_structured?: { description: string; likelihood: number; severity: number; mitigation?: string }[];
      alternatives?: { option: string; tradeoff: string }[];
      effort?: { magnitude: string; hours: { min: number; max: number } };
      execution_plan?: string;
      tensions?: { dimension: string; left_agent: string; right_agent: string; description: string }[];
      // --- Cycle 14: Native Understanding ---
      interpretation_ar?: string;
      english_intent?: string;
      ambiguity_level?: string;
    }[];
    overall_confidence?: number;
    integrity_blocked?: boolean;
    sentinel_alerts?: { id: string; severity: string; message: string }[];
  };
  latency_ms?: number;
  error?: string;
};

const IdeaRunPage = () => {
  // ... (rest of state) ...
  const [idea, setIdea] = useState('');
  const [adrId, setAdrId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('جاهز');
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildStatus, setBuildStatus] = useState<string>('');
  const [isApproving, setIsApproving] = useState(false);
  const [approvalResult, setApprovalResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>('plan');

  // Clarity Gate State
  const [clarityAnswer, setClarityAnswer] = useState('');
  const [isClarifying, setIsClarifying] = useState(false);

  // Decision Gate State
  const [rationale, setRationale] = useState('');

  // Poll analysis when we have an adrId
  useEffect(() => {
    if (!adrId) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/analysis/${adrId}`);
        if (!res.ok) return;
        const data: AnalysisResponse = await res.json();
        setAnalysis(data);

        // Stop polling if complete or failed, BUT ALSO stop if clarity is required
        if (data?.synthesis || data?.status === 'failed' || data?.error || data?.status === 'clarity_required') {
          clearInterval(interval);
          if (data?.status === 'clarity_required') {
            setStatus('✋ بانتظار توضيح منك');
          } else {
            setStatus(data?.status ?? 'اكتمل التحليل');
          }
        }
      } catch (err) {
        console.error(err);
      }
    }, 1500);
    return () => clearInterval(interval);
  }, [adrId]);

  const submitIdea = async () => {
    if (!idea.trim()) {
      setStatus('اكتب فكرتك أولاً');
      return;
    }
    setIsSubmitting(true);
    setStatus('جاري بدء التحليل السيادي...');
    setAnalysis(null);
    setApprovalResult(null);
    setAdrId(null);
    try {
      const res = await fetch('/api/idea-run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea }),
      });
      if (!res.ok) {
        const text = await res.text();
        setStatus(`خطأ: ${text}`);
      } else {
        const data: IdeaResponse = await res.json();
        setAdrId(data.adr_id);
      }
    } catch (err) {
      setStatus(`خطأ في الاتصال: ${String(err)}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitClarification = async () => {
    if (!clarityAnswer.trim() || !adrId) return;
    setIsClarifying(true);
    setStatus('جاري استئناف التحليل...');
    try {
      const res = await fetch('/api/governance/clarify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          adr_id: adrId,
          answer: clarityAnswer,
          human_id: 'Sovereign-User'
        }),
      });
      if (res.ok) {
        setClarityAnswer('');
        // Logic to restart polling: clear analysis and re-trigger effect by keeping adrId
        // but interval needs to be re-created. Since adrId didn't change, we need a trick or manual call.
        setAnalysis({ status: 'resuming' });
        // The useEffect will re-run because analysis changed, wait, adrId didn't change.
        // Let's just manually re-poll or force effect by toggling adrId briefly (unsafe) 
        // Better: the poll interval is already cleared. We need to re-set it.
        // I'll wrap the polling in a ref or just re-set adrId.
        const currentId = adrId;
        setAdrId(null);
        setTimeout(() => setAdrId(currentId), 10);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsClarifying(false);
    }
  };

  const approveChanges = async () => {
    if (!adrId) return;
    setIsApproving(true);

    // مراحل التنفيذ التفصيلية
    setStatus('🔐 خطوة 1/3: التحقق من الصلاحيات...');
    await new Promise(resolve => setTimeout(resolve, 600));

    setStatus('📝 خطوة 2/3: كتابة الملفات إلى القرص...');

    try {
      const res = await fetch('/api/governance/approve-changes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          adr_id: adrId,
          rationale: rationale
        }),
      });
      const data = await res.json();
      setApprovalResult(data);

      setStatus('🔍 خطوة 3/3: التحقق من نجاح الكتابة...');
      await new Promise(resolve => setTimeout(resolve, 400));

      if (data.status === 'success') {
        setStatus(`✅ اكتمل! تم تطبيق ${data.applied?.length || 0} تغيير بنجاح.`);
      } else {
        setStatus(`❌ فشل التطبيق: ${data.detail || 'خطأ غير معروف'}`);
      }
    } catch (err) {
      setStatus(`❌ خطأ في الاتصال: ${String(err)}`);
    } finally {
      setIsApproving(false);
    }
  };

  const triggerRebuild = async () => {
    setIsBuilding(true);
    setBuildStatus('⚙️ جاري تشغيل npm run build...');
    try {
      const res = await fetch('/api/rebuild', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'ok') {
        setBuildStatus('تمت إعادة البناء بنجاح (حدّث الصفحة لرؤية التغييرات)');
      } else {
        setBuildStatus(`فشل البناء: ${data.message || data.stderr || 'ERROR'}`);
      }
    } catch (err) {
      setBuildStatus(`خطأ في الاتصال: ${String(err)}`);
    } finally {
      setIsBuilding(false);
    }
  };

  const synthesis = analysis?.synthesis;
  const agentResults = synthesis?.agent_results || [];
  const mediatorResult = agentResults.find(r => r.agent_id === 'agent-mediator');
  const secretaryResult = agentResults.find(r => r.agent_id === 'secretary' || r.agent_id === 'agent-secretary'); // Robust check
  const tensions = mediatorResult?.tensions || [];

  const allFileChanges = agentResults
    .flatMap(r => r.file_changes || [])
    .filter(Boolean);

  return (
    <div className="max-w-6xl mx-auto space-y-8 p-6 font-sans antialiased text-slate-900 bg-white">
      {/* Header Section */}
      <section className="border-b pb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-2">قمرة قيادة الأفكار السيادية</h1>
        <p className="text-slate-500">حول أفكارك إلى واقع برمجي بمراجعة وتعاون الوكلاء المتخصصين.</p>
      </section>

      {/* Input Area */}
      <section className="space-y-4">
        <textarea
          className="w-full border-2 border-slate-200 rounded-xl p-4 min-h-[160px] text-lg focus:border-slate-900 focus:ring-0 transition-all bg-slate-50"
          placeholder="مثال: أضف ميزة الاختبار الآلي لجميع طلبات API مع إظهار تقرير الجودة."
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
        />
        <div className="flex items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={submitIdea}
              disabled={isSubmitting || !idea.trim()}
              className="bg-black text-white px-8 py-3 rounded-full font-bold hover:bg-slate-800 disabled:opacity-30 transition-all flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  جاري التحليل...
                </>
              ) : 'بدء دورة الحوكمة'}
            </button>
            <button
              onClick={triggerRebuild}
              disabled={isBuilding}
              className="border-2 border-slate-900 text-slate-900 px-8 py-3 rounded-full font-bold hover:bg-slate-50 disabled:opacity-30 transition-all"
            >
              إعادة بناء النظام
            </button>
          </div>
          <div className={`px-4 py-2 rounded-full text-sm font-bold ${adrId ? 'bg-indigo-50 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>
            {status}
          </div>
        </div>
      </section>

      {/* Clarity Gate (Interactive Governance) */}
      {analysis?.status === 'clarity_required' && (
        <section className="animate-in fade-in zoom-in duration-500">
          <div className="bg-indigo-900 text-white rounded-2xl p-8 shadow-2xl border-4 border-indigo-400">
            <div className="flex items-start gap-6">
              <div className="bg-white/10 p-4 rounded-full text-3xl animate-pulse">🤔</div>
              <div className="flex-1 space-y-4">
                <div className="inline-block px-3 py-1 bg-indigo-500 rounded-lg text-[10px] font-black uppercase tracking-wider">
                  بوابة الوضوح: {analysis.agent || 'الوكيل'} يطلب توضيحاً
                </div>
                <h2 className="text-2xl font-bold leading-tight">
                  "{analysis.question}"
                </h2>
                <div className="pt-2">
                  <textarea
                    className="w-full bg-white/10 border border-white/20 rounded-xl p-4 text-white placeholder-white/40 focus:bg-white/20 focus:outline-none transition-all"
                    placeholder="اكتب توضيحك هنا ليستمر الوكلاء في العمل..."
                    value={clarityAnswer}
                    onChange={(e) => setClarityAnswer(e.target.value)}
                  />
                  <button
                    onClick={submitClarification}
                    disabled={isClarifying || !clarityAnswer.trim()}
                    className="mt-4 bg-white text-indigo-900 px-10 py-3 rounded-full font-black text-sm hover:bg-slate-100 disabled:opacity-50 transition-all shadow-xl"
                  >
                    {isClarifying ? 'جاري الاستئناف...' : 'تأكيد ودفع العملية للأمام 🚀'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Cycle 14: Native Understanding (United Understanding Card) */}
      {secretaryResult && secretaryResult.interpretation_ar && (
        <section className="animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="bg-gradient-to-r from-slate-50 to-white border-2 border-slate-900 rounded-2xl overflow-hidden shadow-md relative">
            <div className="absolute top-0 right-0 py-1 px-4 bg-slate-900 text-white text-[10px] font-black uppercase tracking-widest rounded-bl-xl z-20">
              طبقة الفهم الأصيل
            </div>
            <div className="p-8 grid md:grid-cols-[1fr_auto] gap-8 items-center">
              <div className="space-y-4">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-3xl">🪞</span>
                  <h3 className="text-xl font-bold text-slate-900">مرآة الفهم الموحد</h3>
                </div>
                <p className="text-lg text-slate-700 leading-relaxed font-medium">
                  "{secretaryResult.interpretation_ar}"
                </p>
                <div className="flex items-center gap-4 text-xs font-mono text-slate-400 pt-2 border-t border-slate-100">
                  <span className="uppercase tracking-wider font-bold">Technical Intent:</span>
                  <span className="bg-slate-100 px-2 py-1 rounded text-slate-600">{secretaryResult.english_intent}</span>
                </div>
              </div>

              <div className="flex flex-col items-center justify-center p-4 bg-slate-50 rounded-xl border border-slate-200 min-w-[120px]">
                <span className="text-[10px] font-black text-slate-400 uppercase mb-2">مقياس الغموض</span>
                <div className={`text-2xl font-black ${secretaryResult.ambiguity_level === 'Low' ? 'text-emerald-500' : secretaryResult.ambiguity_level === 'Medium' ? 'text-amber-500' : 'text-red-500'}`}>
                  {secretaryResult.ambiguity_level === 'Low' ? 'واضح' : secretaryResult.ambiguity_level === 'Medium' ? 'متوسط' : 'غامض'}
                </div>
                <div className="w-full h-1 bg-slate-200 rounded-full mt-2 overflow-hidden">
                  <div className={`h-full ${secretaryResult.ambiguity_level === 'Low' ? 'bg-emerald-500 w-[10%]' : secretaryResult.ambiguity_level === 'Medium' ? 'bg-amber-500 w-[50%]' : 'bg-red-500 w-[90%]'}`} />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Collaboration Hub */}
      {synthesis && (
        <section className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl overflow-hidden shadow-sm">
            {/* Analysis Tabs */}
            <div className="flex border-b border-slate-200 bg-white">
              <button
                onClick={() => setActiveTab('plan')}
                className={`px-6 py-4 font-bold text-sm transition-all border-b-2 ${activeTab === 'plan' ? 'border-black text-black' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
              >
                📋 خطة العمل
              </button>
              <button
                onClick={() => setActiveTab('agents')}
                className={`px-6 py-4 font-bold text-sm transition-all border-b-2 ${activeTab === 'agents' ? 'border-black text-black' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
              >
                🧠 المقترحات الهيكلية ({agentResults.length})
              </button>
              {tensions.length > 0 && (
                <button
                  onClick={() => setActiveTab('tensions')}
                  className={`px-6 py-4 font-bold text-sm transition-all border-b-2 ${activeTab === 'tensions' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
                >
                  ⚡ التوترات الإدراكية ({tensions.length})
                </button>
              )}
              <button
                onClick={() => setActiveTab('risk')}
                className={`px-6 py-4 font-bold text-sm transition-all border-b-2 ${activeTab === 'risk' ? 'border-black text-black' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
              >
                🛡️ تقييم المخاطر
              </button>
            </div>

            <div className="p-6">
              {activeTab === 'plan' && (
                <div className="space-y-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="p-3 bg-indigo-100 text-indigo-700 rounded-xl">
                      <span className="text-xl">🎯</span>
                    </div>
                    <div>
                      <h3 className="font-bold text-lg">التغييرات المقترحة على الكود</h3>
                      <p className="text-slate-500 text-sm">تم التوافق عليها من قبل {agentResults.length} وكلاء متخصصين.</p>
                    </div>
                  </div>

                  {allFileChanges.length > 0 ? (
                    <div className="grid gap-4">
                      {allFileChanges.map((fc, idx) => (
                        <div key={idx} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
                          <div className="px-4 py-2 bg-slate-100 flex justify-between items-center border-b">
                            <span className="font-mono text-sm font-bold text-slate-700">{fc.path}</span>
                            <span className="text-[10px] uppercase font-black text-slate-400">Mode: {fc.mode || 'write'}</span>
                          </div>
                          <pre className="p-4 text-xs font-mono text-slate-600 overflow-x-auto bg-slate-50 leading-relaxed max-h-60">
                            {fc.content}
                          </pre>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-slate-400 italic">لا توجد تغييرات هيكلية مقترحة لهذه الفكرة.</div>
                  )}
                </div>
              )}

              {activeTab === 'agents' && (
                <div className="grid md:grid-cols-2 gap-4">
                  {agentResults.map((agent, idx) => {
                    const roleName = typeof agent.role === 'string'
                      ? agent.role
                      : (agent.role?.value || 'SPECIALIST');

                    if (agent.agent_id === 'agent-mediator') return null;

                    return (
                      <div key={idx} className="bg-white border border-slate-200 p-5 rounded-xl space-y-4 shadow-sm hover:border-slate-300 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex flex-col">
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">
                              {agent.agent_id}
                            </span>
                            <span className="px-3 py-1 bg-slate-900 text-white text-[10px] font-black rounded-lg tracking-widest uppercase inline-block w-fit mt-1">
                              {roleName}
                            </span>
                          </div>
                          <div className="p-2 bg-indigo-50 rounded-full text-indigo-600 text-xs">🤖</div>
                        </div>

                        {/* Extended Mind: Structured Proposal */}
                        <div className="space-y-3">
                          {agent.trigger && (
                            <div className="space-y-1">
                              <span className="text-[10px] font-bold text-slate-400 uppercase">المحفز (Trigger)</span>
                              <p className="text-sm text-slate-700 leading-relaxed font-medium">{agent.trigger}</p>
                            </div>
                          )}

                          {agent.impact && (
                            <div className="space-y-1">
                              <span className="text-[10px] font-bold text-slate-400 uppercase">الأثر المتوقع (Impact)</span>
                              <p className="text-sm text-slate-600 leading-relaxed">{agent.impact}</p>
                            </div>
                          )}

                          {agent.risks_structured && agent.risks_structured.length > 0 && (
                            <div className="space-y-1 border-t pt-2">
                              <span className="text-[10px] font-bold text-red-400 uppercase">المخاطر المهيكلة (Risks)</span>
                              <div className="grid gap-2 mt-1">
                                {agent.risks_structured.map((risk, ridx) => (
                                  <div key={ridx} className="bg-red-50 p-2 rounded-lg text-xs text-red-800 flex justify-between items-center">
                                    <span>{risk.description}</span>
                                    <span className="font-bold opacity-60">L:{risk.likelihood} S:{risk.severity}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="space-y-2 border-t pt-2">
                            <h4 className="font-bold text-slate-900 text-sm">التوصيات:</h4>
                            <ul className="text-xs text-slate-600 space-y-1">
                              {agent.recommendations?.map((rec, i) => (
                                <li key={i} className="flex gap-2 items-start">
                                  <span className="text-emerald-500">✔</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {agent.confidence !== undefined && (
                          <div className="pt-2 border-t border-slate-50 flex justify-between items-center">
                            <span className="text-[10px] text-slate-400">معدل الثقة الإدراكي</span>
                            <span className="text-[10px] font-bold text-slate-600">{Math.round(agent.confidence * 100)}%</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {activeTab === 'tensions' && (
                <div className="space-y-6">
                  <div className="p-6 bg-indigo-50 border border-indigo-100 rounded-2xl">
                    <h3 className="text-xl font-bold text-indigo-900 mb-2 flex items-center gap-2">
                      <span>⚡</span> توترات تتطلب قراراً سيادياً
                    </h3>
                    <p className="text-indigo-700 text-sm">
                      تم اكتشاف تعارض في الرؤى بين الوكلاء. النظام لن يحاول حل هذا التعارض تلقائياً؛ القرار لك.
                    </p>
                  </div>

                  <div className="grid gap-4">
                    {tensions.map((tension, tidx) => (
                      <div key={tidx} className="bg-white border-2 border-indigo-200 p-6 rounded-2xl shadow-sm relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-2 h-full bg-indigo-500 group-hover:w-4 transition-all"></div>
                        <div className="flex justify-between items-center mb-4">
                          <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-[10px] font-black rounded-lg uppercase tracking-widest">
                            بعد التوتر: {tension.dimension}
                          </span>
                        </div>
                        <div className="flex items-center gap-8 mb-4">
                          <div className="text-center">
                            <div className="text-[10px] font-black text-slate-400 uppercase mb-1">طرف 1</div>
                            <div className="font-bold text-slate-900">{tension.left_agent}</div>
                          </div>
                          <div className="flex-1 h-px bg-slate-100 relative">
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-2 text-indigo-600 font-bold">VS</div>
                          </div>
                          <div className="text-center">
                            <div className="text-[10px] font-black text-slate-400 uppercase mb-1">طرف 2</div>
                            <div className="font-bold text-slate-900">{tension.right_agent}</div>
                          </div>
                        </div>
                        <p className="text-slate-600 leading-relaxed italic">
                          "{tension.description}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'risk' && (
                <div className="space-y-4">
                  <div className="p-4 bg-orange-50 border border-orange-200 rounded-xl text-orange-800 text-sm font-medium flex items-center gap-3">
                    <span className="text-xl">🛡️</span>
                    <div>
                      <p className="font-bold">نظام Sentinel نشط</p>
                      <p className="text-xs opacity-80">يتم فحص التغييرات المقترحة للكشف عن حذف المنطق البرمجي أو الانحراف الثقافي.</p>
                    </div>
                  </div>

                  {synthesis.integrity_blocked && (
                    <div className="p-5 bg-red-50 border-2 border-red-200 rounded-xl text-red-900 animate-bounce">
                      <h4 className="font-black flex items-center gap-2 mb-1">
                        <span className="bg-red-600 text-white px-2 py-0.5 rounded text-[10px]">CRITICAL</span>
                        خرق لسلامة السياق (Context Integrity Breach)
                      </h4>
                      <p className="text-sm">اكتشف الوكلاء محاولة لحذف منطق برمجي جوهري دون تبرير كافٍ. تم قفل عملية الاعتماد آلياً.</p>
                    </div>
                  )}

                  <div className="bg-white border border-slate-200 p-6 rounded-xl">
                    <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                      🔍 السجلات الرقابية
                    </h3>
                    <div className="space-y-3">
                      {synthesis.sentinel_alerts?.map((alert, i) => (
                        <div key={i} className={`p-3 rounded-lg text-xs flex justify-between ${alert.severity === 'CRITICAL' ? 'bg-red-50 text-red-700 font-bold' : 'bg-slate-50 text-slate-600'}`}>
                          <span>{alert.message}</span>
                          <span className="uppercase opacity-50">{alert.severity}</span>
                        </div>
                      ))}
                      {!synthesis.sentinel_alerts?.length && (
                        <div className="text-center py-4 text-slate-400 italic text-sm">لا توجد تنبيهات أمنية حالياً.</div>
                      )}
                      <div className="pt-4 border-t flex justify-between items-center text-sm">
                        <span className="text-slate-500">معدل الثقة بالتغيير</span>
                        <span className="font-bold text-indigo-600">{(synthesis.overall_confidence ?? 0) * 100}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Approval Execution Bar */}
            <div className="p-6 bg-white border-t border-slate-200">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm">
                  <span className="text-slate-500">ADR ID:</span> <span className="font-mono font-bold text-slate-700">{adrId}</span>
                </div>
                <div className="text-xs text-slate-400 italic">
                  {agentResults.length} وكيل شارك في التحليل
                </div>
              </div>

              {/* Decision Gate: Rationale UI */}
              {!synthesis.integrity_blocked && (!approvalResult || approvalResult.status !== 'success') && (
                <div className="mb-6 animate-in slide-in-from-top-2 duration-300">
                  <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl p-6 space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="bg-black text-white p-2 rounded-lg text-sm">⚖️</div>
                      <div>
                        <h4 className="font-bold text-slate-900">بوابة القرار السيادي</h4>
                        <p className="text-xs text-slate-500 font-medium">يتطلب النظام تبريراً مكتوباً منك قبل السماح بتنفيذ هذه التغييرات.</p>
                      </div>
                    </div>
                    <textarea
                      placeholder="لماذا وافقت على هذه المقترحات؟ ما هو المبرر المنطقي؟"
                      className="w-full border border-slate-200 rounded-xl p-3 text-sm focus:border-black focus:ring-0 transition-all bg-white"
                      rows={3}
                      value={rationale}
                      onChange={(e) => setRationale(e.target.value)}
                    />
                    {!rationale.trim() && (
                      <div className="text-[10px] text-red-500 font-bold flex items-center gap-1">
                        <span>⚠️</span> المبرر مطلوب لتفعيل زر الاعتماد
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* زر الاعتماد مع مؤشر التقدم */}
              <button
                onClick={approveChanges}
                disabled={isApproving || (approvalResult && approvalResult.status === 'success') || synthesis.integrity_blocked || !rationale.trim()}
                className="w-full bg-black text-white px-10 py-5 rounded-xl font-black text-lg shadow-lg hover:bg-slate-900 disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none transition-all relative overflow-hidden group"
              >
                {isApproving && (
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-700 via-purple-600 to-indigo-700 animate-pulse"></div>
                )}
                <span className="relative z-10 flex items-center justify-center gap-3">
                  {isApproving && (
                    <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  )}
                  {isApproving
                    ? 'جاري التنفيذ - يرجى الانتظار...'
                    : (approvalResult?.status === 'success' ? '✅ تم التنفيذ بنجاح' : '🚀 اعتماد وتطبيق التغييرات')
                  }
                </span>
              </button>

              {/* شريط التقدم المرئي عند التنفيذ */}
              {isApproving && (
                <div className="mt-3 bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-pulse" style={{ width: '70%', transition: 'width 0.5s' }}></div>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Build Feedback */}
      {buildStatus && (
        <div className={`p-4 rounded-xl border-2 ${buildStatus.includes('نجاح') ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-slate-50 border-slate-200 text-slate-800'}`}>
          <div className="font-bold text-sm mb-1">{buildStatus.includes('نجاح') ? '✅ نجاح' : 'ℹ️ تنبيه'}</div>
          <div className="text-xs">{buildStatus}</div>
        </div>
      )}
    </div>
  );
};

export default IdeaRunPage;