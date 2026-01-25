
import PolicyEditor from '@web-ui/components/admin/PolicyEditor';

const SCPPolicies = () => {
    return (
        <div className="h-full flex flex-col gap-4 animate-in fade-in duration-500 overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-800">📋 Governance Policy Hub</h3>
                <span className="px-2 py-1 rounded-lg bg-emerald-50 text-emerald-600 text-[10px] font-black uppercase">Enforced</span>
            </div>
            <div className="flex-1 min-h-0 overflow-y-auto pr-2 custom-scrollbar">
                <PolicyEditor />
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.05); border-radius: 10px; }
            `}} />
        </div>
    );
};

export default SCPPolicies;
