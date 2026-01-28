import { useMutation, useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from '@tanstack/react-router';
import { ArrowRight, BookOpen, Bot, CheckCircle2, MessageSquare, PieChart, Terminal } from 'lucide-react';
import type { ReactNode } from 'react';
import { useState } from 'react';
import { fetchAgentsRegistry } from '../../../shared/api/system';
import { AgentChat } from '../../../shared/features/agent/AgentChat';
import { AgentPortfolioTab } from '../../../shared/features/agent/AgentPortfolioTab';
import { AgentRoleTab } from '../../../shared/features/agent/AgentRoleTab';
import { useSCPStream } from '../../../shared/hooks/useSCPStream';
import { runAgent } from '../api';
import type { AgentRunResult, AgentsRegistryResponse } from '../types';

export default function AgentPage() {
  const router = useRouter();
  const { agentId } = useParams({ from: '/agent/$agentId' });
  const { connection } = useSCPStream();
  const [activeTab, setActiveTab] = useState<'portfolio' | 'chat' | 'role' | 'overview'>('portfolio');

  const { data } = useQuery<AgentsRegistryResponse>({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
  });

  const agent = data?.agents.find((a) => a.id === agentId);

  const runMutation = useMutation<{ status: string; agent: string; result?: AgentRunResult }, Error>({
    mutationKey: ['run-agent', agentId],
    mutationFn: () =>
      runAgent(agent?.role || agent?.id || 'unknown', {
        title: `Run ${agent?.name || 'Unknown'}`,
        context: `Manual run from Console`,
      }),
  });

  if (!agent) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <h2 className="text-xl font-bold text-slate-700">Agent Not Found</h2>
        <button className="text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1" onClick={() => router.navigate({ to: '/dashboard' })}>
          <ArrowRight className="w-4 h-4" /> Back to Thought Space
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 pt-4 max-w-7xl mx-auto pb-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <button className="flex items-center gap-1 text-indigo-600 hover:text-indigo-700 font-semibold" onClick={() => router.navigate({ to: '/dashboard' })}>
          <ArrowRight className="w-4 h-4" /> رجوع
        </button>
        <span className="text-slate-400">/</span>
        <span className="text-slate-600 font-medium">{agent.department}</span>
      </div>

      {/* Hero Header */}
      <section className="glass rounded-3xl p-6 space-y-4 border border-slate-200/50 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-emerald-400 to-indigo-500 opacity-20"></div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-400 border border-slate-100">
              <Bot className="w-8 h-8" />
            </div>
            <div>
              <p className="text-xs text-indigo-500 font-bold tracking-wider uppercase mb-1">{agent.department}</p>
              <h2 className="text-3xl font-bold text-slate-900 tracking-tight">{agent.name}</h2>
              <div className="flex items-center gap-2 mt-2">
                <span className={`px-2 py-0.5 text-[10px] uppercase font-bold rounded-full border ${agent.status === 'active' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                  {agent.status}
                </span>
                <span className={`px-2 py-0.5 text-[10px] uppercase font-bold rounded-full border ${connection === 'open' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                  {connection === 'open' ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <button
              className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium flex items-center gap-2 shadow-sm transition-all active:scale-95"
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
            >
              <CheckCircle2 className="w-4 h-4" />
              {runMutation.isPending ? 'Processing...' : 'Run Diagnostics'}
            </button>
            <span className="text-[10px] text-slate-400 font-mono">ID: {agent.id}</span>
          </div>
        </div>
      </section>

      {/* Agent Run Result Area (Live Output) */}
      {runMutation.data?.result && (
        <div className="p-6 rounded-2xl bg-emerald-50 border border-emerald-100 animate-in slide-in-from-top-4 fade-in duration-500 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-bold text-emerald-900 flex items-center gap-2 text-lg">
              <CheckCircle2 className="w-5 h-5" /> Diagnostics Result
            </h4>
            <button
              onClick={() => runMutation.reset()}
              className="text-xs text-emerald-700 hover:text-emerald-900 underline"
            >
              Dismiss
            </button>
          </div>
          <div className="prose prose-sm prose-emerald max-w-none">
            <div className="whitespace-pre-wrap text-slate-800 leading-relaxed font-sans bg-white/50 p-4 rounded-xl border border-emerald-100/50">
              {runMutation.data.result.analysis}
            </div>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-1">
        <TabButton active={activeTab === 'portfolio'} onClick={() => setActiveTab('portfolio')} icon={<PieChart className="w-4 h-4" />} label="Portfolio & Stats" />
        <TabButton active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} icon={<MessageSquare className="w-4 h-4" />} label="Live Chat" />
        <TabButton active={activeTab === 'role'} onClick={() => setActiveTab('role')} icon={<Terminal className="w-4 h-4" />} label="System Role" />
        <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} icon={<BookOpen className="w-4 h-4" />} label="Profile & Specs" />
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'portfolio' && <AgentPortfolioTab agentId={agent.id} />}
        {activeTab === 'role' && <AgentRoleTab agentId={agent.id} />}

        {activeTab === 'chat' && (
          <div className="grid lg:grid-cols-4 gap-6">
            <div className="lg:col-span-3">
              <AgentChat agentId={agentId} />
            </div>
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <h4 className="font-bold text-slate-700 text-sm mb-2">Chat Guidance</h4>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Use this channel to directly query the agent's internal knowledge base or test specific prompts.
                  Queries here do not affect the main governance consensus.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="glass rounded-2xl p-6 border border-slate-200/60">
                <h3 className="font-bold text-slate-800 mb-4">Functional Description</h3>
                <p className="text-slate-600 leading-relaxed">{agent.description}</p>
              </div>
              <div className="glass rounded-2xl p-6 border border-slate-200/60">
                <h3 className="font-bold text-slate-800 mb-4">Capabilities</h3>
                <div className="grid sm:grid-cols-2 gap-3">
                  {agent.capabilities.map((cap) => (
                    <div key={cap} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <div className="w-2 h-2 rounded-full bg-indigo-500" />
                      <span className="text-sm font-medium text-slate-700">{cap}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="space-y-6">
              <div className="glass rounded-2xl p-6 border border-slate-200/60">
                <h3 className="font-bold text-slate-800 mb-4">Signal Feed</h3>
                <div className="flex flex-wrap gap-2">
                  {(agent.signals || ['No live signals']).map((signal) => (
                    <span key={signal} className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 font-mono text-xs border border-slate-200">
                      {signal}
                    </span>
                  ))}
                </div>
              </div>
              <div className="glass rounded-2xl p-6 border border-slate-200/60">
                <h3 className="font-bold text-slate-800 mb-2">Fidelity Score</h3>
                <div className="text-4xl font-black text-slate-900 mb-1">{agent.fidelity}</div>
                <p className="text-xs text-slate-400">Model alignment score based on recent performance.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: ReactNode; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`
                px-4 py-3 rounded-t-xl text-sm font-bold flex items-center gap-2 border-b-2 transition-all
                ${active
          ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50'
          : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50'}
            `}
    >
      {icon}
      {label}
    </button>
  );
}
