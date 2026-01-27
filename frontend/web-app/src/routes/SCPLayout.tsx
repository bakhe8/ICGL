import { Outlet } from '@tanstack/react-router';
import { Radio } from 'lucide-react';

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



            {/* Local Area Content */}
            <main className="flex-1 bg-white border border-slate-200 rounded-3xl shadow-sm p-6 overflow-hidden relative min-h-[500px]">
                <Outlet />
            </main>
        </div>
    );
};



export default SCPLayout;
