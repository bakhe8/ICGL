import { useQuery } from '@tanstack/react-query';
import { Activity, AlertTriangle, Clock, Search, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { fetchPatternAlerts } from '../api';

import AccessControlMatrix from '../../../shared/features/system/AccessControlMatrix';

export default function SecurityPage() {
    const [toast, setToast] = useState<string | null>(null);

    const { data: alertsData } = useQuery({
        queryKey: ['pattern-alerts'],
        queryFn: () => fetchPatternAlerts(20), // Fetch more for the dedicated page
        retry: 1,
        staleTime: 20_000,
    });

    const alerts = alertsData?.alerts ?? [];

    return (
        <div className="space-y-6 pt-4">
            {toast && (
                <div className="fixed top-3 right-3 z-50 px-4 py-2 rounded-lg bg-emerald-600 text-white shadow-panel text-sm">
                    {toast}
                    <button className="ml-2 text-xs underline" onClick={() => setToast(null)}>إغلاق</button>
                </div>
            )}

            {/* Mandate 4: Sovereign Matrix (RBAC) */}
            <section className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <AccessControlMatrix />
            </section>

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

