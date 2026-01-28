import { Lock, Shield, Unlock } from 'lucide-react';

type Role = 'Sovereign' | 'Architect' | 'Agent' | 'Observer';
type Resource = 'Event Bus' | 'File System' | 'Memory (R)' | 'Memory (W)' | 'Deployment';

const MATRIX: Record<Role, Resource[]> = {
    'Sovereign': ['Event Bus', 'File System', 'Memory (R)', 'Memory (W)', 'Deployment'],
    'Architect': ['Event Bus', 'File System', 'Memory (R)', 'Memory (W)'],
    'Agent': ['Event Bus', 'Memory (R)'],
    'Observer': ['Event Bus', 'Memory (R)'],
};

export default function AccessControlMatrix() {
    const roles: Role[] = ['Sovereign', 'Architect', 'Agent', 'Observer'];
    const resources: Resource[] = ['Event Bus', 'File System', 'Memory (R)', 'Memory (W)', 'Deployment'];

    return (
        <div className="glass rounded-3xl p-6 relative overflow-hidden">
            <header className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-indigo-600" />
                        Access Control Matrix (RBAC)
                    </h2>
                    <p className="text-xs text-slate-500">Security Mandate Enforcement (backend/security/rbac.py)</p>
                </div>
            </header>

            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="text-left text-slate-500 border-b border-slate-200">
                            <th className="py-3 px-4 font-mono font-medium">ROLE</th>
                            {resources.map(r => (
                                <th key={r} className="py-3 px-4 font-mono font-medium text-center text-xs uppercase tracking-wider">{r}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {roles.map(role => (
                            <tr key={role} className="border-b border-slate-50 last:border-0 hover:bg-white/40 transition-colors">
                                <td className="py-4 px-4 font-bold text-slate-700">{role}</td>
                                {resources.map(resource => {
                                    const hasAccess = MATRIX[role].includes(resource);
                                    return (
                                        <td key={resource} className="py-4 px-4 text-center">
                                            <div className={`inline-flex items-center justify-center w-8 h-8 rounded-full ${hasAccess ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-300'
                                                }`}>
                                                {hasAccess ? <Unlock className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
                                            </div>
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
