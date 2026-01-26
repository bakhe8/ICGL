
import { Activity, Database, ShieldAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { ADR, SystemStatus } from '../api/types';

const GovernanceLabPage = () => {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [adrs, setAdrs] = useState<ADR[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const baseUrl = 'http://127.0.0.1:8000';
                const [statusRes, adrRes] = await Promise.all([
                    fetch(`${baseUrl}/status`),
                    fetch(`${baseUrl}/kb/adrs`)
                ]);
                setStatus(await statusRes.json());
                setAdrs(await adrRes.json());
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="w-12 h-12 rounded-full border-4 border-slate-200 border-t-indigo-600 animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col gap-2">
                <h1 className="text-4xl font-black text-slate-900 tracking-tight">Governance Lab | مختبر الحوكمة</h1>
                <p className="text-slate-500 font-medium italic">Experimental supervision of the Sovereign Intelligence Core.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Integrity Card */}
                <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col gap-6 relative overflow-hidden group hover:scale-[1.02] transition-transform duration-500">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-indigo-500/10 transition-colors" />
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-200">
                            <ShieldAlert size={24} />
                        </div>
                        <div>
                            <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest">System Integrity</h3>
                            <p className="text-2xl font-black text-slate-900">{status?.active_alert_level || 'Checking...'}</p>
                        </div>
                    </div>
                    <div className="flex flex-col gap-2">
                        <div className="text-[10px] font-bold text-slate-400 flex justify-between uppercase">
                            <span>Policy Conformance</span>
                            <span>98.4%</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-600 rounded-full w-[98.4%]" />
                        </div>
                    </div>
                </div>

                {/* Drift Card */}
                <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col gap-6 relative overflow-hidden group hover:scale-[1.02] transition-transform duration-500">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-emerald-500/10 transition-colors" />
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-white shadow-lg shadow-emerald-200">
                            <Activity size={24} />
                        </div>
                        <div>
                            <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest">Policy Drift</h3>
                            <p className="text-2xl font-black text-slate-900">{status?.telemetry.drift_detection_count ?? 0} Events</p>
                        </div>
                    </div>
                    <p className="text-xs text-slate-500 font-medium">Monitoring deviation from established architecture rules.</p>
                </div>

                {/* Decisions Card */}
                <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col gap-6 relative overflow-hidden group hover:scale-[1.02] transition-transform duration-500">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-purple-500/10 transition-colors" />
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-purple-600 flex items-center justify-center text-white shadow-lg shadow-purple-200">
                            <Database size={24} />
                        </div>
                        <div>
                            <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest">ADR Records</h3>
                            <p className="text-2xl font-black text-slate-900">{adrs.length} Decisions</p>
                        </div>
                    </div>
                    <p className="text-xs text-slate-500 font-medium">Historical record of all architecturally significant choices.</p>
                </div>
            </div>

            <div className="bg-slate-900 rounded-[3rem] p-12 text-white relative overflow-hidden shadow-2xl">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] -mr-32 -mt-32" />
                <div className="relative flex flex-col items-center text-center gap-6">
                    <div className="px-4 py-1.5 rounded-full bg-white/10 border border-white/20 text-[10px] font-black uppercase tracking-[0.2em]">Sovereign Control Layer</div>
                    <h2 className="text-5xl font-black tracking-tighter max-w-2xl leading-[1.1]">The Mind is Under Constant Supervision.</h2>
                    <p className="text-slate-400 max-w-xl text-lg font-medium leading-relaxed">
                        ICGL ensures that every agent interaction, memory modification, and code execution aligns with the high-fidelity goals of the Sovereign Intelligence.
                    </p>
                    <div className="flex gap-4 mt-4">
                        <button className="px-8 py-4 bg-white text-slate-900 rounded-2xl font-black text-sm hover:scale-105 transition-transform shadow-xl">MANAGE POLICIES</button>
                        <button className="px-8 py-4 bg-white/5 border border-white/10 text-white rounded-2xl font-black text-sm hover:bg-white/10 transition-colors">VIEW TRACES</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GovernanceLabPage;
