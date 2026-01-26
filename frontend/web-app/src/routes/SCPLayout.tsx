/* eslint-disable @typescript-eslint/no-explicit-any */

import { Link, Outlet } from '@tanstack/react-router';
import { Activity, BarChart3, Code2, MessageSquareText, Network, Radio, ShieldAlert } from 'lucide-react';

const SCPLayout = () => {
    return (
        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-700">
            {/* SCP Header */}
            <div className="flex items-center justify-between bg-white p-6 rounded-3xl border border-slate-200 shadow-sm relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-full bg-gradient-to-l from-indigo-500/5 to-transparent" />
                <div className="flex items-center gap-4 relative">
                    <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-200 group-hover:rotate-12 transition-transform duration-500">
                        <Radio className="w-6 h-6 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Sovereign Control Plane (SCP) | مستوى التحكم السيادي</h1>
                        <p className="text-slate-500 text-xs italic font-medium">Real-time supervision and anomaly detection for swarm intelligence.</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-bold border border-emerald-100 uppercase">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        Network Online
                    </span>
                </div>
            </div>

            {/* SCP Sub-navigation Sub-sidebar */}
            <div className="flex gap-6 min-h-[calc(100vh-20rem)]">
                <aside className="w-64 flex flex-col gap-1">
                    <SCPNavLink to="/admin/scp/overview" icon={BarChart3} label="Overview | نظرة عامة" />
                    <SCPNavLink to="/admin/scp/events" icon={Activity} label="Live Events | الأحداث الحية" />
                    <SCPNavLink to="/admin/scp/channels" icon={Network} label="Channels | قنوات الاتصال" />
                    <SCPNavLink to="/admin/scp/traces" icon={Code2} label="Process Traces | تتبع العمليات" />
                    <SCPNavLink to="/admin/scp/policies" icon={ShieldAlert} label="Policies | حزمة السياسات" />
                    <div className="my-2 border-t border-slate-100" />
                    <SCPNavLink to="/admin/scp/coc" icon={MessageSquareText} label="Coordination Hub (COC)" />
                </aside>

                {/* Local Area Content */}
                <main className="flex-1 bg-white border border-slate-200 rounded-3xl shadow-sm p-6 overflow-hidden relative">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

const SCPNavLink = ({ to, icon: Icon, label }: { to: string, icon: any, label: string }) => (
    <Link
        to={to}
        className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-indigo-600 transition-all group [&.active]:bg-indigo-600 [&.active]:text-white [&.active]:shadow-lg active:scale-95 text-xs font-bold"
        activeProps={{ className: 'active' }}
    >
        <Icon size={16} className="group-hover:scale-110 transition-transform" />
        <span>{label}</span>
    </Link>
);

export default SCPLayout;
