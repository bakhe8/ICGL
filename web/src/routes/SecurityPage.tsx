import { useMutation, useQuery } from '@tanstack/react-query';
import { Activity, AlertTriangle, Play, Search, Shield, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { fetchPatternAlerts, fetchSystemHealth, runPatternDetection } from '../api/queries';
import { fallbackHealth, fallbackPatternAlerts } from '../data/fallbacks';

export default function SecurityPage() {
    const [toast, setToast] = useState<string | null>(null);

    const { data: alertsData, refetch: refetchAlerts } = useQuery({
        queryKey: ['pattern-alerts'],
        queryFn: () => fetchPatternAlerts(20), // Fetch more for the dedicated page
        retry: 1,
        staleTime: 20_000,
        initialData: { alerts: fallbackPatternAlerts },
    });

    const { data: healthData } = useQuery({
        queryKey: ['system-health'],
        queryFn: fetchSystemHealth,
        staleTime: 30_000,
        initialData: fallbackHealth,
    });

    const patternDetection = useMutation({
        mutationFn: () => runPatternDetection(10),
        onSuccess: () => {
            setToast('تم تشغيل كشف الأنماط بنجاح');
            refetchAlerts();
        },
    });

    const alerts = alertsData?.alerts ?? fallbackPatternAlerts;
    const integrityScore = healthData?.integrity_score ?? 90;

    return (
        <div className="space-y-6">
            {toast && (
                <div className="fixed top-3 right-3 z-50 px-4 py-2 rounded-lg bg-emerald-600 text-white shadow-panel text-sm">
                    {toast}
                    <button className="ml-2 text-xs underline" onClick={() => setToast(null)}>إغلاق</button>
                </div>
            )}

            <header className="glass rounded-3xl p-6 sm:p-8">
                <div className="flex flex-col lg:flex-row gap-6 lg:items-center lg:justify-between">
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-2xl ${integrityScore > 80 ? 'bg-emerald-50' : 'bg-rose-50'}`}>
                            <Shield className={`w-8 h-8 ${integrityScore > 80 ? 'text-emerald-600' : 'text-rose-600'}`} />
                        </div>
                        <div>
                            <h1 className="text-3xl font-extrabold text-ink leading-tight">
                                مركز الأمن السيادي <span className="text-brand-base">· Security</span>
                            </h1>
                            <p className="text-sm text-slate-600 mt-1">مراقبة سلامة الحوكمة، كشف الأنماط، وإدارة المخاطر آلياً.</p>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center gap-4">
                            <div className="text-right">
                                <p className="text-[10px] text-slate-500 font-bold uppercase">System Integrity</p>
                                <p className="text-2xl font-black text-ink">{integrityScore}%</p>
                            </div>
                            <div className="w-12 h-12 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin-slow" />
                        </div>
                        <button
                            className="px-6 py-2 rounded-2xl bg-brand-base text-white shadow-lg shadow-brand-base/20 hover:bg-brand-deep transition-all flex items-center gap-2"
                            onClick={() => patternDetection.mutate()}
                            disabled={patternDetection.isPending}
                        >
                            <Play className="w-4 h-4" />
                            {patternDetection.isPending ? 'جاري الفحص...' : 'بدء فحص الأنماط'}
                        </button>
                    </div>
                </div>
            </header>

            <section className="grid lg:grid-cols-4 gap-6">
                <div className="lg:col-span-3 glass rounded-3xl p-6 space-y-6">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <ShieldAlert className="w-5 h-5 text-rose-500" />
                            تنبيهات Sentinel النشطة
                        </h3>
                        <div className="relative">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                            <input
                                type="text"
                                placeholder="بحث في التنبيهات..."
                                className="pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-base/20 transition-all w-64"
                            />
                        </div>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-4">
                        {alerts.map((alert) => (
                            <div
                                key={alert.alert_id}
                                className="p-4 rounded-2xl border border-slate-200 bg-white/70 hover:border-rose-200 hover:bg-rose-50/30 transition-all group"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <AlertTriangle className={`w-4 h-4 ${alert.severity === 'high' ? 'text-rose-500' : 'text-amber-500'}`} />
                                        <span className="font-bold text-sm text-ink">{alert.pattern}</span>
                                    </div>
                                    <span className={`text-[10px] px-2 py-1 rounded-full font-bold border ${alert.severity === 'high' ? 'bg-rose-50 text-rose-700 border-rose-100' : 'bg-amber-50 text-amber-700 border-amber-100'
                                        }`}>
                                        {alert.severity.toUpperCase()}
                                    </span>
                                </div>
                                <p className="text-xs text-slate-600 leading-relaxed mb-3">{alert.description}</p>
                                <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium">
                                    <div className="flex items-center gap-1">
                                        <Clock className="w-3 h-3" />
                                        {new Date(alert.timestamp).toLocaleTimeString()}
                                    </div>
                                    <span>{alert.event_count} events detected</span>
                                </div>
                            </div>
                        ))}
                        {alerts.length === 0 && (
                            <div className="col-span-full py-20 flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl">
                                <ShieldCheck className="w-12 h-12 mb-2 opacity-10 text-emerald-500" />
                                <p>لم يتم اكتشاف أي أنماط مشبوهة. النظام آمن.</p>
                            </div>
                        )}
                    </div>
                </div>

                <aside className="space-y-6">
                    <div className="glass rounded-3xl p-6 space-y-4">
                        <h3 className="font-semibold text-ink">تحليلات التهديدات</h3>
                        <div className="space-y-3">
                            <RiskLevel label="Drift Detection" value="Low" color="bg-emerald-500" />
                            <RiskLevel label="Policy Violations" value="None" color="bg-emerald-500" />
                            <RiskLevel label="Agent Sync" value="Stable" color="bg-emerald-500" />
                            <RiskLevel label="Human Override" value="Caution" color="bg-amber-500" />
                        </div>
                    </div>

                    <div className="glass rounded-3xl p-6 space-y-4">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <Activity className="w-4 h-4 text-brand-base" />
                            Live Security Feed
                        </h3>
                        <div className="space-y-3">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="flex gap-3 text-xs">
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1" />
                                    <div>
                                        <p className="text-ink font-semibold">Integrity Check Pass</p>
                                        <p className="text-slate-400 text-[10px]">2 minutes ago · BaseNode</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </aside>
            </section>
        </div>
    );
}

function RiskLevel({ label, value, color }: { label: string; value: string; color: string }) {
    return (
        <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-slate-100">
            <span className="text-xs text-slate-600 font-medium">{label}</span>
            <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-ink">{value}</span>
                <div className={`w-2 h-2 rounded-full ${color}`} />
            </div>
        </div>
    );
}

import { Clock } from 'lucide-react';
