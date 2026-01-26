import { ShieldCheck, Users } from 'lucide-react';
import AtomicLogViewer from '../components/system/AtomicLogViewer';
import NervousSystemMonitor from '../components/system/NervousSystemMonitor';

export default function OperationsPage() {
    return (
        <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
            {/* Header */}
            <header className="flex flex-col gap-2">
                <div className="flex items-center gap-2 mb-1">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                    <p className="text-[10px] font-black text-rose-500 uppercase tracking-widest">Sovereign Core</p>
                </div>
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight">System Soul (Operations)</h1>
                <p className="text-slate-500 max-w-2xl leading-relaxed">
                    Monitor the autonomic nervous system, atomic transaction logs, and core committee pulses.
                </p>
            </header>

            {/* Nervous Sytem (Top) */}
            <section className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <NervousSystemMonitor />
            </section>

            {/* Grid: Atomic Logs vs Committee */}
            <section className="grid lg:grid-cols-3 gap-6">

                {/* Left: Atomic Log */}
                <div className="lg:col-span-2 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
                    <AtomicLogViewer />
                </div>

                {/* Right: Committee Status (Placeholder for Phase 3 Real Data) */}
                <div className="lg:col-span-1 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
                    <div className="glass rounded-3xl p-6">
                        <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
                            <Users className="w-5 h-5 text-indigo-600" />
                            Committee Pulse
                        </h3>
                        <div className="space-y-3">
                            <MemberStatus name="Architect" role="System Design" status="Thinking" />
                            <MemberStatus name="Sovereign" role="Policy Guard" status="Active" isActive />
                            <MemberStatus name="DevOps" role="Transaction Ops" status="Standing By" />
                        </div>
                    </div>

                    <div className="glass rounded-3xl p-6 bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100">
                        <h3 className="font-bold text-emerald-800 flex items-center gap-2 mb-2">
                            <ShieldCheck className="w-5 h-5" />
                            Health Status
                        </h3>
                        <div className="text-3xl font-black text-emerald-600 mb-1">98.2%</div>
                        <p className="text-xs text-emerald-700">System Integrity Optimal</p>
                    </div>
                </div>
            </section>
        </div>
    );
}

function MemberStatus({ name, role, status, isActive }: { name: string; role: string; status: string; isActive?: boolean }) {
    return (
        <div className="flex items-center justify-between p-3 rounded-2xl bg-white/50 border border-slate-100">
            <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${isActive ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'}`}>
                    {name[0]}
                </div>
                <div>
                    <p className="text-sm font-bold text-slate-700">{name}</p>
                    <p className="text-[10px] text-slate-400">{role}</p>
                </div>
            </div>
            <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${isActive ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-400'}`}>
                {status}
            </span>
        </div>
    )
}
