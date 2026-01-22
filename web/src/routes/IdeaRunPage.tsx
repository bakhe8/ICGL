import { useEffect, useState } from 'react';

type IdeaResponse = { status: string; adr_id: string };
type AnalysisResponse = {
  status?: string;
  synthesis?: {
    agent_results: {
      role?: { value?: string };
      recommendations?: string[];
      concerns?: string[];
      file_changes?: { path: string; content: string; mode?: string }[];
    }[];
    overall_confidence?: number;
  };
  latency_ms?: number;
  error?: string;
};

const IdeaRunPage = () => {
  const [idea, setIdea] = useState('');
  const [adrId, setAdrId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('جاهز');
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildStatus, setBuildStatus] = useState<string>('');

  // Poll analysis when we have an adrId
  useEffect(() => {
    if (!adrId) return;
    const interval = setInterval(async () => {
      try {
        // استخدم المسار عبر الـ proxy (/api) لضمان الوصول للسيرفر الخلفي
        const res = await fetch(`/api/analysis/${adrId}`);
        if (!res.ok) return;
        const data: AnalysisResponse = await res.json();
        setAnalysis(data);
        if (data?.synthesis || data?.status === 'failed' || data?.error) {
          clearInterval(interval);
          setStatus(data?.status ?? 'اكتمل');
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
    setStatus('يتم الإرسال والتشغيل...');
    setAnalysis(null);
    try {
      // استخدم المسار عبر الـ proxy (/api) لضمان الوصول للسيرفر الخلفي
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
        setStatus('جاري التحليل والتنفيذ...');
      }
    } catch (err) {
      setStatus(`خطأ في الاتصال: ${String(err)}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const triggerRebuild = async () => {
    setIsBuilding(true);
    setBuildStatus('جاري إعادة البناء...');
    try {
      const res = await fetch('/api/rebuild', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'ok') {
        setBuildStatus('تمت إعادة البناء بنجاح (حدّث الصفحة لرؤية التغييرات)');
      } else if (data.status === 'busy') {
        setBuildStatus('إعادة بناء أخرى قيد التنفيذ. انتظر قليلاً.');
      } else {
        setBuildStatus(`فشل البناء: ${data.message || data.stderr || data.code}`);
      }
    } catch (err) {
      setBuildStatus(`خطأ في الاتصال: ${String(err)}`);
    } finally {
      setIsBuilding(false);
    }
  };

  const fileChanges =
    analysis?.synthesis?.agent_results
      ?.flatMap((r) => r.file_changes || [])
      ?.filter(Boolean) || [];

  return (
    <div className="p-6 space-y-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold">تشغيل فكرة وتنفيذها تلقائياً</h1>
      <p className="text-sm text-gray-500">
        اكتب ما تريد إنجازه بلغة طبيعية. سيحوّل النظام الفكرة إلى مهمة، يشغّل الوكلاء، ثم ينفذ التغييرات.
      </p>

      <textarea
        className="w-full border rounded p-3 min-h-[140px] focus:outline-none focus:ring"
        placeholder="مثال: أضف صفحة تعرض سجل التشغيل الأخير وتخزن النتائج في ملف JSON."
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
      />

      <div className="flex items-center gap-3">
        <button
          onClick={submitIdea}
          disabled={isSubmitting}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {isSubmitting ? 'جارٍ الإرسال...' : 'تشغيل الفكرة'}
        </button>
        <span className="text-sm text-gray-700">{status}</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={triggerRebuild}
          disabled={isBuilding}
          className="bg-slate-800 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {isBuilding ? 'جارٍ إعادة البناء...' : 'إعادة بناء الواجهة'}
        </button>
        {buildStatus && <span className="text-sm text-gray-700">{buildStatus}</span>}
      </div>

      {adrId && (
        <div className="p-3 border rounded bg-gray-50">
          <div className="text-sm text-gray-600">ADR ID: {adrId}</div>
        </div>
      )}

      {analysis?.error && (
        <div className="p-3 border border-red-200 bg-red-50 text-red-700 rounded">
          {analysis.error}
        </div>
      )}

      {analysis?.synthesis && (
        <div className="space-y-3 p-4 border rounded">
          <div className="font-semibold">
            النتيجة: {status} — الثقة: {(analysis.synthesis.overall_confidence ?? 0) * 100}%
          </div>

          {fileChanges.length > 0 ? (
            <div>
              <div className="font-semibold mb-2">التغييرات المقترحة/المنفذة:</div>
              <ul className="space-y-2 text-sm">
                {fileChanges.map((fc, idx) => (
                  <li key={`${fc.path}-${idx}`} className="p-2 border rounded bg-white">
                    <div className="font-mono text-blue-700">{fc.path}</div>
                    <div className="text-xs text-gray-500">وضع: {fc.mode || 'write'}</div>
                    <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto max-h-40">
{fc.content}
                    </pre>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="text-sm text-gray-600">لا توجد تغييرات ملفات ظاهرة بعد.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default IdeaRunPage;
