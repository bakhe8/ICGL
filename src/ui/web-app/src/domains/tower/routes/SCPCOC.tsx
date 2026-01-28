
import Chat from '@shared-features/admin/Chat';

const SCPCOC = () => {
    return (
        <div className="h-full flex flex-col gap-4 animate-in fade-in duration-500 overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-800">💬 Coordination Hub (COC)</h3>
                <span className="px-2 py-1 rounded-lg bg-indigo-50 text-indigo-600 text-[10px] font-black uppercase">Low Latency</span>
            </div>
            <div className="flex-1 min-h-0">
                <Chat />
            </div>
        </div>
    );
};

export default SCPCOC;
