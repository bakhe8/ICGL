import { Network, Zap } from 'lucide-react';
import { useState } from 'react';
import TechnicalCapabilities from '../components/TechnicalCapabilities';
import AgentsFlowPage from './AgentsFlowPage/AgentsFlowPage';

export default function RegistryPage() {
    const [activeTab, setActiveTab] = useState<'flow' | 'capabilities'>('flow');

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
                        <Network className="w-8 h-8 text-indigo-500" />
                        Sovereign Registry
                    </h1>
                    <p className="text-slate-500">Manage active agents, monitor workflow flow, and review capability gaps.</p>
                </div>
                <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                    <button
                        onClick={() => setActiveTab('flow')}
                        className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${activeTab === 'flow' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500 hover:text-slate-700'}`}
                    >
                        <Zap className="w-4 h-4" />
                        Active Flow & Agents
                    </button>
                    <button
                        onClick={() => setActiveTab('capabilities')}
                        className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${activeTab === 'capabilities' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500 hover:text-slate-700'}`}
                    >
                        <Network className="w-4 h-4" />
                        Capabilities Matrix
                    </button>
                </div>
            </header>

            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                {activeTab === 'flow' ? (
                    <AgentsFlowPage />
                ) : (
                    <div className="glass rounded-3xl p-6">
                        <TechnicalCapabilities />
                    </div>
                )}
            </div>
        </div>
    );
}
