import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { AlertCircle, CheckCircle2, Play, Shield, Users, Zap } from 'lucide-react';
import { useState } from 'react';
import { runPatternDetection } from '../api/queries';
import { ExecutiveConsole } from '../components/executive/ExecutiveConsole';
import { CouncilSimResult } from '../components/governance/CouncilSimResult';

interface PatternResults {
    analyzed_events: number;
    alerts: Array<{ message?: string; type: string }>;
}

interface SimulationData {
    topic: string;
    results: any[];
}

const GovernanceLabPage = () => {
    const [testInput, setTestInput] = useState('');
    const [results, setResults] = useState<PatternResults | null>(null);
    const [simTopic, setSimTopic] = useState('');
    const [simResults, setSimResults] = useState<SimulationData | null>(null);
    const [isSimulating, setIsSimulating] = useState(false);

    const detector = useMutation({
        mutationFn: () => runPatternDetection(),
        onSuccess: (data) => setResults(data),
    });

    const runSimulation = async () => {
        if (!simTopic) return;
        setIsSimulating(true);
        try {
            const resp = await axios.post('/api/governance/simulate-council', {
                topic: simTopic,
                context: "Full council deliberation requested via Governance Lab."
            });
            setSimResults(resp.data);
        } catch (err) {
            console.error(err);
        } finally {
            setIsSimulating(false);
        }
    };

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between border-b pb-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                        <Shield className="text-brand-base" /> مختبر الحوكمة — Governance Lab
                    </h1>
                    <p className="text-slate-500">اختبار السياسات، كشف الأنماط، ومحاكاة القرارات السيادية.</p>
                </div>
            </header>

            <div className="grid md:grid-cols-2 gap-6">
                <section className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                    <h2 className="font-bold flex items-center gap-2">
                        <Play className="w-4 h-4 text-emerald-500" /> مـكتب الاختبار
                    </h2>
                    <textarea
                        className="w-full h-48 p-4 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-base outline-none text-sm"
                        placeholder="أدخل نصاً أو قطعة برمجية لاختبار مطابقتها للسياسات..."
                        value={testInput}
                        onChange={(e) => setTestInput(e.target.value)}
                    />
                    <button
                        onClick={() => detector.mutate()}
                        disabled={detector.isPending}
                        className="w-full py-3 bg-brand-base text-white rounded-xl font-bold hover:bg-brand-deep transition-colors disabled:opacity-50"
                    >
                        {detector.isPending ? 'جاري الفحص...' : 'تشغيل فحص الأنماط (Pattern Detection)'}
                    </button>
                </section>

                <section className="bg-slate-50 p-6 rounded-2xl border border-slate-200 border-dashed space-y-4">
                    <h2 className="font-bold flex items-center gap-2 text-slate-600">
                        <Activity className="w-4 h-4" /> نتائج الفحص الحي
                    </h2>

                    {!results && !detector.isPending && (
                        <div className="h-48 flex items-center justify-center text-slate-400 text-sm italic">
                            بانتظار تشغيل الاختبار...
                        </div>
                    )}

                    {detector.isPending && (
                        <div className="h-48 flex items-center justify-center">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-base"></div>
                        </div>
                    )}

                    {results && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-slate-200">
                                <span className="text-sm font-medium">الأحداث المحللة:</span>
                                <span className="font-mono text-brand-base">{results.analyzed_events}</span>
                            </div>
                            <div className="space-y-2">
                                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">التنبيهات المكتشفة</p>
                                {results.alerts.length === 0 ? (
                                    <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg flex items-center gap-2 text-sm border border-emerald-100">
                                        <CheckCircle2 className="w-4 h-4" /> لم يتم العثور على انتهاكات للسياسات.
                                    </div>
                                ) : (
                                    results.alerts.map((alert: any, i: number) => (
                                        <div key={i} className="p-3 bg-rose-50 text-rose-700 rounded-lg flex items-center gap-2 text-sm border border-rose-100">
                                            <AlertCircle className="w-4 h-4" /> {alert.message || alert.type}
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}
                </section>
            </div>

            <section className="bg-gradient-to-br from-slate-900 to-indigo-950 p-8 rounded-3xl text-white shadow-xl space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-3">
                            <Users className="text-indigo-400" /> مـركز محاكاة المجلس السيادي (Sovereign Council Hub)
                        </h2>
                        <p className="text-slate-400 text-sm">استدعاء الـ 27 وكيلاً دفعة واحدة لاختبار الرؤية الشاملة للمشروع.</p>
                    </div>
                    <div className="px-4 py-2 bg-indigo-500/10 rounded-full border border-indigo-500/20 text-indigo-400 text-xs font-mono">
                        Status: Phase 8 Controlled Simulation Gateway
                    </div>
                </div>

                <div className="flex gap-4">
                    <input
                        className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-indigo-500 transition-all placeholder:text-slate-600"
                        placeholder="ما هو موضوع النقاش الذي تريد طرحه على المجلس؟ (مثال: مستقبل واجهة المستخدم 2026)"
                        value={simTopic}
                        onChange={(e) => setSimTopic(e.target.value)}
                    />
                    <button
                        onClick={runSimulation}
                        disabled={isSimulating || !simTopic}
                        className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-bold flex items-center gap-2 transition-all disabled:opacity-50 shadow-lg shadow-indigo-600/20"
                    >
                        {isSimulating ? (
                            <>
                                <Zap className="w-4 h-4 animate-spin" /> جاري المحاكاة...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4" /> بدء المحاكاة الجماعية
                            </>
                        )}
                    </button>
                </div>

                {simResults && (
                    <div className="pt-6 border-t border-white/10 mt-6">
                        <CouncilSimResult results={simResults.results} topic={simResults.topic} />
                    </div>
                )}
            </section>

            <section className="bg-slate-900 p-8 rounded-3xl text-white shadow-xl space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-3">
                            <Shield className="text-indigo-400" /> مـكتب التحكم التنفيذي (Executive Control)
                        </h2>
                        <p className="text-slate-400 text-sm">قناة تواصل مباشرة مع وكيلك التنفيذي لإصدار الأوامر وتوقيع القرارات.</p>
                    </div>
                </div>

                <ExecutiveConsole />
            </section>
        </div>
    );
};

const Activity = ({ className }: { className?: string }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
);

export default GovernanceLabPage;
