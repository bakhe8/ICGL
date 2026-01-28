import { useQuery } from '@tanstack/react-query';
import { FileCode, Shield, Terminal } from 'lucide-react';
import { fetchAgentRole } from '../../../domains/hall/api';

export function AgentRoleTab({ agentId }: { agentId: string }) {

    // Fetch Role Definition
    const roleQuery = useQuery({
        queryKey: ['agent-role', agentId],
        queryFn: async () => {
            // Clean the ID (remove 'agent-' prefix for cleaner lookup if needed, but backend handles loose match)
            return await fetchAgentRole(agentId);
        }
    });

    if (roleQuery.isLoading) {
        return <div className="p-8 text-center text-slate-400">Loading Configuration...</div>;
    }

    const roleData = roleQuery.data;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">

            <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 flex items-start gap-3">
                <Shield className="w-5 h-5 text-indigo-600 mt-0.5" />
                <div>
                    <h4 className="font-bold text-indigo-900 text-sm">Review Policy</h4>
                    <p className="text-xs text-indigo-700 mt-1 leading-relaxed">
                        This definition is the <strong>source of truth</strong> loaded directly from the backend agent registry.
                        Changing the python class methods or system prompt will reflect here immediately after a server restart.
                    </p>
                </div>
            </div>

            <section className="glass rounded-2xl overflow-hidden border border-slate-200/60">
                <div className="bg-slate-900 p-4 flex items-center justify-between border-b border-slate-700">
                    <div className="flex items-center gap-2 text-slate-200">
                        <Terminal className="w-4 h-4 text-emerald-400" />
                        <span className="font-mono text-xs font-bold">System Prompt / Role Definition</span>
                    </div>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded font-mono">
                        {roleData?.role_name || 'UNKNOWN'}.py
                    </span>
                </div>

                <div className="p-6 bg-slate-900 text-slate-300 font-mono text-xs leading-relaxed overflow-x-auto">
                    <pre className="whitespace-pre-wrap">
                        {roleData?.role_definition || 'No definition found.'}
                    </pre>
                </div>
            </section>

            <div className="flex justify-end">
                <button
                    onClick={() => roleQuery.refetch()}
                    className="text-xs text-slate-400 hover:text-indigo-600 flex items-center gap-1 transition-colors"
                >
                    <FileCode className="w-3 h-3" /> Refresh Definition
                </button>
            </div>
        </div>
    );
}
