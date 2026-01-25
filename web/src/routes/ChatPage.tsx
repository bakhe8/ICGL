import { useMutation, useQuery } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Activity,
  Cpu,
  Database,
  FileCode,
  RefreshCw,
  Send,
  ShieldCheck,
  Terminal,
  X,
  Zap
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { fetchSystemHealth, runAITerminal, sendFreeChatMessage, writeAIFile } from '../api/queries';
import type { ChatMessage, ChatResponse, ToolCall } from '../api/types';
import Mermaid from '../components/Mermaid';
import { SovereignTerminal } from '../components/terminal/SovereignTerminal';

interface NeuralAction {
  cmd: string;
  path?: string;
  status: string; // Changed from literal to string to match ToolCall
  output?: string;
}

const SovereignNeuralAction = ({ actions }: { actions: NeuralAction[] }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 p-4 rounded-3xl bg-indigo-500/5 border border-indigo-500/20 backdrop-blur-md overflow-hidden relative group"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-50" />
      <div className="flex items-center gap-2 mb-3 relative z-10">
        <Zap className="w-3 h-3 text-indigo-400 animate-pulse" />
        <span className="text-[9px] font-black text-indigo-400 uppercase tracking-widest">Neural Execution Thread</span>
      </div>
      <div className="space-y-2 relative z-10">
        {actions.map((action, i) => (
          <div key={i} className="flex items-center justify-between gap-4 py-1.5 border-b border-indigo-500/10 last:border-0">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                {action.cmd === 'read' ? <Activity className="w-3 h-3 text-indigo-400" /> :
                  action.cmd === 'write' ? <FileCode className="w-3 h-3 text-emerald-400" /> :
                    <Database className="w-3 h-3 text-amber-400" />}
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] font-bold text-white/80 font-mono tracking-tight">{action.cmd}</span>
                <span className="text-[9px] text-white/40 font-mono truncate max-w-[200px]">{action.path || 'system'}</span>
              </div>
            </div>
            <div className={`px-2 py-0.5 rounded-full text-[8px] font-bold uppercase tracking-wider ${action.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
              action.status === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
              }`}>
              {action.status}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default function ChatPage() {
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatSession, setChatSession] = useState<string | undefined>(undefined);
  const [autoExecute] = useState(true);
  const [pendingToolCalls, setPendingToolCalls] = useState<ToolCall[]>([]);
  const [isExecutingTools, setIsExecutingTools] = useState(false);
  const [commandLog, setCommandLog] = useState<string | null>(null);
  const [showTerminal, setShowTerminal] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement | null>(null);

  useQuery({
    queryKey: ['system-health'],
    queryFn: fetchSystemHealth,
    refetchInterval: 5000,
    refetchIntervalInBackground: true,
    staleTime: 15_000,
    placeholderData: (prev) => prev,
  });

  const chatMutation = useMutation({
    mutationFn: async (input: string) => {
      if (!input.trim()) throw new Error('اكتب رسالة');
      const historyContext = chatHistory.map((msg) => `${msg.role}: ${msg.content || msg.text}`).join('\n');
      return sendFreeChatMessage({
        message: input.trim(),
        session_id: chatSession,
        extra_context: historyContext,
        auto_execute: autoExecute,
        actor: 'owner',
      });
    },
    onSuccess: (res: ChatResponse, variables) => {
      const incoming: ChatMessage[] = res.messages?.length
        ? (res.messages as ChatMessage[])
        : [
          { role: 'user', content: variables, text: variables },
          { role: 'assistant', content: res.text || '...', text: res.text || '...' },
        ];
      setChatHistory((prev) => [...prev, ...incoming]);
      setChatSession((prev) => prev || (res.state as { session_id?: string })?.session_id);
      if (res.blocked_commands?.length) setPendingToolCalls(res.blocked_commands);
      if (res.executed?.length) {
        const executedLog = res.executed
          .map((r: ToolCall) => `${r.cmd}: ${r.output || r.status}`)
          .join('\n');
        setCommandLog(executedLog);
      }
      setChatInput('');
    },
  });

  const submitChat = () => {
    if (!chatInput.trim()) return;
    chatMutation.mutate(chatInput.trim());
  };

  useEffect(() => {
    const el = chatScrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [chatHistory]);

  const renderArtifact = (msg: ChatMessage) => {
    const content = msg.content || msg.text || '';

    // 1. Mermaid Rendering
    const mermaidMatch = content.match(/```mermaid\n([\s\S]*?)```/);
    if (mermaidMatch) {
      return (
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 text-[10px] font-bold text-indigo-400 uppercase tracking-widest px-1">
            <Activity className="w-3 h-3" />
            <span>Visual Reasoning Engine</span>
          </div>
          <Mermaid chart={mermaidMatch[1]} />
          <div className="prose prose-invert prose-sm max-w-none text-slate-400">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content.replace(/```mermaid\n[\s\S]*?```/, '')}</ReactMarkdown>
          </div>
        </div>
      );
    }

    // 2. Governance ADR Artifact
    if (content.includes('[[GOVERNANCE_ADR]]')) {
      const adrTitle = content.match(/Title:\s*(.*)/i)?.[1] || 'New Proposal';
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-6 rounded-3xl border-indigo-500/30 bg-indigo-500/5"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest border border-indigo-500/20 px-2 py-1 rounded-lg">Status: Awaiting Review</span>
          </div>
          <h3 className="text-lg font-bold text-white mb-2">{adrTitle}</h3>
          <div className="prose prose-invert prose-sm text-slate-400 mb-6">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content.replace('[[GOVERNANCE_ADR]]', '')}</ReactMarkdown>
          </div>
        </motion.div>
      );
    }

    // 3. Command Parsing & Sequential Narrative
    const commandRegex = /\[\[COMMANDS\]\][\s\S]*?\[\[\/COMMANDS\]\]/g;
    const parts = content.split(commandRegex);
    const commandMatches = content.match(/\[\[COMMANDS\]\]([\s\S]*?)\[\[\/COMMANDS\]\]/);

    const initialThought = parts[0]?.trim();
    const followUpResult = parts[1]?.trim();

    let actions: NeuralAction[] = [];
    if (commandMatches) {
      const block = commandMatches[1];
      actions = block.split('\n').filter(l => l.trim() && !l.startsWith('#')).map(line => {
        const p = line.split('|');
        return {
          cmd: (p[0] || 'cmd').trim().toLowerCase(),
          path: p[1]?.trim(),
          status: 'ok',
        } as NeuralAction;
      });
    }

    return (
      <div className="space-y-6">
        {/* Phase 1: Contextual Explanation */}
        {initialThought && (
          <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-code:text-indigo-300">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{initialThought}</ReactMarkdown>
          </div>
        )}

        {/* Phase 2: Integrated Execution Block */}
        {actions.length > 0 && <SovereignNeuralAction actions={actions} />}

        {/* Phase 3: Post-Execution Narrative */}
        {followUpResult && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="prose prose-invert prose-sm max-w-none pt-4 border-t border-white/5 opacity-80 italic"
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{followUpResult}</ReactMarkdown>
          </motion.div>
        )}
      </div>
    );
  };

  const executePendingTools = async () => {
    if (!pendingToolCalls.length) return;
    setIsExecutingTools(true);
    const results: string[] = [];
    try {
      for (const call of pendingToolCalls) {
        const cmd = call.proposed || call;
        if (cmd.cmd === 'cmd') {
          const cmdPath = cmd.path || '';
          const res = await runAITerminal({ cmd: cmd.content || '' });
          results.push(`cmd ${cmdPath}: ${res.output}`);
        } else if (cmd.cmd === 'write') {
          await writeAIFile({ path: cmd.path || '', content: cmd.content || '' });
          results.push(`write ${cmd.path || ''}: saved`);
        }
      }
      setCommandLog(results.join('\n'));
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Execution failed';
      setCommandLog(errorMsg);
    } finally {
      setPendingToolCalls([]);
      setIsExecutingTools(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 font-['Cairo']">
      {/* Main Chat Workspace */}
      <main className="flex-1 flex flex-col min-w-0 bg-white/[0.01]">

        {pendingToolCalls.length > 0 && (
          <div className="mx-8 mt-4 p-4 rounded-2xl border border-amber-300 bg-amber-50/80 text-amber-900 shadow-sm space-y-2">
            <div className="flex items-center justify-between gap-2">
              <div className="font-semibold text-sm">تأكيد أوامر حساسة قبل التنفيذ</div>
              <span className="text-[11px] px-2 py-1 rounded-full bg-white border border-amber-200">
                {pendingToolCalls.length} أمر بانتظار الموافقة
              </span>
            </div>
            <div className="space-y-1 text-xs">
              {pendingToolCalls.map((cmd, idx) => (
                <div key={idx} className="flex items-center justify-between bg-white px-3 py-2 rounded-lg border border-amber-200 text-amber-800">
                  <span className="font-mono">{cmd.proposed?.cmd || cmd.cmd} | {cmd.proposed?.path || cmd.path}</span>
                  <span className="text-amber-600">{cmd.output || 'Requires approval'}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-end gap-2">
              <button
                className="px-3 py-1.5 rounded-lg border border-amber-200 bg-white text-amber-700 text-xs"
                onClick={() => setPendingToolCalls([])}
                disabled={isExecutingTools}
              >
                رفض
              </button>
              <button
                className="px-4 py-1.5 rounded-lg bg-amber-600 text-white text-xs disabled:opacity-50"
                onClick={executePendingTools}
                disabled={isExecutingTools}
              >
                {isExecutingTools ? 'تنفيذ...' : 'تأكيد التنفيذ'}
              </button>
            </div>
          </div>
        )}

        {commandLog && (
          <div className="mx-8 mt-3 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs">
            {commandLog}
          </div>
        )}

        {/* Chat Stream */}
        <div ref={chatScrollRef} className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar relative">
          {showTerminal && (
            <div className="absolute top-8 right-8 z-20 w-[420px] h-[360px] bg-slate-950/90 border border-white/10 rounded-2xl shadow-2xl backdrop-blur-xl overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 border-b border-white/10 text-xs text-white/70 bg-slate-900/60">
                <span className="flex items-center gap-2"><Terminal className="w-4 h-4" /> منفذ أوامر مباشر</span>
                <button onClick={() => setShowTerminal(false)} className="p-1 rounded hover:bg-white/10" aria-label="Close Terminal">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="h-[310px]">
                <SovereignTerminal />
              </div>
            </div>
          )}
          <AnimatePresence initial={false}>
            {chatHistory.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-indigo-500/5 flex items-center justify-center border border-indigo-500/10 mb-8 animate-pulse">
                  <Cpu className="w-12 h-12 text-indigo-500/20" />
                </div>
                <h3 className="text-3xl font-black text-white italic tracking-tighter uppercase mb-2 opacity-10">Sovereign Executive Console | لوحة القيادة التنفيذية</h3>
                <p className="text-[10px] text-indigo-300/30 font-bold uppercase tracking-[0.3em]">Governed AI Execution Engine | محرك التنفيذ المحكوم ذكياً</p>
                <div className="mt-8 p-6 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl max-w-md text-center animate-in fade-in zoom-in duration-1000">
                  <h4 className="text-indigo-400 font-bold mb-2">Sovereign Control Node Active</h4>
                  <p className="text-white/40 text-[11px] leading-relaxed">
                    هذه الواجهة مخصصة للتحكم الكامل في المشروع. يمكنك إصدار أوامر تنفيذية، إنشاء مقترحات حوكمة، وإدارة نظام ICGL بالكامل.
                  </p>
                </div>
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  transition={{ type: 'spring', damping: 20, stiffness: 100 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[85%] ${msg.role === 'user' ? 'w-full max-w-[500px]' : 'w-full'}`}>
                    <div className={`relative px-8 py-7 rounded-[2.5rem] shadow-2xl ${msg.role === 'user'
                      ? 'bg-gradient-to-br from-indigo-600 to-violet-700 text-white shadow-[0_20px_50px_-15px_rgba(79,70,229,0.4)] ml-auto rounded-tr-lg'
                      : 'bg-white/[0.03] border border-white/10 text-slate-200 rounded-tl-lg backdrop-blur-3xl ring-1 ring-white/5'
                      }`}>
                      {renderArtifact(msg)}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>

        {/* Command Input Area */}
        <footer className="p-8 pb-10 relative">
          <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-t from-slate-950 to-transparent -translate-y-full pointer-events-none" />
          <div className="relative max-w-4xl mx-auto group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/30 to-emerald-500/30 rounded-[3rem] blur opacity-0 group-focus-within:opacity-100 transition duration-1000" />
            <textarea
              className="relative w-full bg-slate-900/40 border border-white/10 focus:border-indigo-500/50 rounded-[2.5rem] px-8 py-6 pr-24 text-white placeholder:text-white/20 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all resize-none min-h-[90px] backdrop-blur-3xl shadow-2xl ring-1 ring-white/5"
              placeholder="Execute command on Sovereign Mind..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), submitChat())}
            />
            <button
              className={`absolute right-4 bottom-4 w-14 h-14 rounded-3xl flex items-center justify-center transition-all ${chatInput.trim() ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/40 hover:scale-110 active:scale-90' : 'bg-white/5 text-white/10 cursor-not-allowed'}`}
              onClick={submitChat}
              disabled={chatMutation.isPending || !chatInput.trim()}
            >
              {chatMutation.isPending ? <RefreshCw className="w-6 h-6 animate-spin text-white/50" /> : <Send className="w-6 h-6" />}
            </button>
          </div>
          <div className="mt-4 flex justify-center gap-6">
            <div className="flex items-center gap-1.5 grayscale opacity-30 hover:grayscale-0 hover:opacity-100 transition-all cursor-default">
              <Activity className="w-3 h-3 text-emerald-400" />
              <span className="text-[9px] text-white font-bold uppercase tracking-widest">Real-time Stream</span>
            </div>
            <div className="flex items-center gap-1.5 grayscale opacity-30 hover:grayscale-0 hover:opacity-100 transition-all cursor-default">
              <ShieldCheck className="w-3 h-3 text-indigo-400" />
              <span className="text-[9px] text-white font-bold uppercase tracking-widest">Signed Proofs</span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
