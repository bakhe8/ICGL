import { useQuery } from '@tanstack/react-query';
import React from 'react';
import { fetchAgentsRegistry } from '../../api/queries';

const OrgSidebar: React.FC = () => {
    const { data, isLoading } = useQuery({
        queryKey: ['agents-registry'],
        queryFn: fetchAgentsRegistry,
        staleTime: 30_000,
    });

    const agents = data?.agents ?? [];

    if (isLoading) {
        return <div className="p-4 text-xs text-slate-400">Loading Agents...</div>;
    }

    return (
        <div className="p-4 bg-slate-50 border-r h-full overflow-y-auto">
            <h2 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Sovereign Agents</h2>
            <ul className="space-y-3">
                {agents.map(agent => (
                    <li key={agent.id} className="group cursor-default">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-slate-700 font-semibold group-hover:text-indigo-600 transition-colors">
                                {agent.name}
                            </span>
                            <span className={`w-2 h-2 rounded-full shadow-sm ${agent.status === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'}`}></span>
                        </div>
                        <p className="text-[10px] text-slate-400 truncate mt-0.5">{agent.role}</p>
                    </li>
                ))}
            </ul>
            {!agents.length && <p className="text-xs text-slate-400 italic mt-4">No agents found.</p>}
        </div>
    );
};

export default OrgSidebar;
