

interface StrategicAdvisorCardProps {
    isAuditing?: boolean;
}

const StrategicAdvisorCard = ({ isAuditing = false }: StrategicAdvisorCardProps) => {
    return (
        <div className={`bg-white rounded-[2rem] p-6 shadow-sm border border-gray-100 flex flex-col justify-between h-48 relative overflow-hidden group transition-all duration-500 ${isAuditing ? 'ring-2 ring-indigo-500/50' : ''}`}>
            <div className="absolute top-0 right-0 p-4 opacity-5">
                <svg className="w-32 h-32" fill="black" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z" /></svg>
            </div>

            <div>
                <h3 className="text-gray-500 text-xs font-bold uppercase tracking-widest mb-1">المستشار الاستراتيجي</h3>
                <div className={`text-2xl font-light text-gray-800 transition-colors ${isAuditing ? 'text-indigo-600' : ''}`}>
                    AI <span className={`font-bold ${isAuditing ? 'text-indigo-600 animate-pulse' : 'text-gray-400'}`}>
                        {isAuditing ? 'Active' : 'Standby'}
                    </span>
                </div>
            </div>

            <div className="relative z-10">
                <div className={`text-sm mb-2 transition-colors ${isAuditing ? 'text-indigo-500 font-medium' : 'text-gray-400'}`}>
                    {isAuditing ? 'Analyzing system coherence...' : 'Waiting for audit request.'}
                </div>

                <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full w-2/3 transition-all duration-1000 ${isAuditing ? 'bg-indigo-500 animate-[shimmer_1.5s_infinite]' : 'bg-gray-300 w-full opacity-20'}`}></div>
                </div>
            </div>
        </div>
    );
};

export default StrategicAdvisorCard;
