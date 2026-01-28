
import NCCIContainer from '@shared-features/admin/Chat/NCCIContainer';

const NCCIPage = () => {
    return (
        <div className="h-[calc(100vh-12rem)] flex flex-col gap-6">
            <div className="flex flex-col gap-1">
                <h1 className="text-2xl font-black text-slate-900 tracking-tight">Neural Core Command (NCCI) | واجهة التحكم في النواة</h1>
                <p className="text-slate-500 text-sm italic">Direct real-time governance link to the Sovereign Intelligence core.</p>
            </div>
            <div className="flex-1 min-h-0 bg-slate-900 rounded-3xl p-6 shadow-2xl shadow-indigo-500/10 border border-indigo-500/20 relative overflow-hidden">
                {/* Abstract background effect */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-[100px] pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/5 blur-[100px] pointer-events-none" />

                <NCCIContainer />
            </div>
        </div>
    );
};

export default NCCIPage;
