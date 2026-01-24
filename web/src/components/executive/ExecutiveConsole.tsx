import axios from 'axios';
import { CheckCircle2, MessageSquare, Send, Shield, Terminal } from 'lucide-react';
import { useState } from 'react';

export function ExecutiveConsole() {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState<any[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [awaitingSign, setAwaitingSign] = useState<any>(null);

    const handleSend = async () => {
        if (!message) return;

        const userMsg = { role: 'user', content: message };
        setChatHistory([...chatHistory, userMsg]);
        setIsProcessing(true);
        setMessage('');

        try {
            const resp = await axios.post('/api/governance/executive/chat', { message: message });
            const agentMsg = {
                role: 'agent',
                content: resp.data.message,
                agent: resp.data.agent_id,
                sentinel: resp.data.sentinel_analysis,
                actionRequired: resp.data.action_required
            };
            setChatHistory(prev => [...prev, agentMsg]);

            if (resp.data.action_required) {
                setAwaitingSign({
                    id: 'PROPOSAL-' + Math.random().toString(36).substr(2, 4).toUpperCase(),
                    description: resp.data.message
                });
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="flex flex-col h-[600px] bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border border-slate-800">
            {/* Header */}
            <div className="p-6 bg-gradient-to-r from-indigo-900 to-slate-900 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-500/20 rounded-xl flex items-center justify-center border border-indigo-500/30">
                        <Shield className="text-indigo-400 w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="text-white font-bold leading-none">Executive Agent</h3>
                        <p className="text-indigo-400 text-[10px] font-mono mt-1 uppercase tracking-widest">Sovereign Human Bridge</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                    <span className="text-slate-400 text-[10px] font-medium uppercase tracking-wider">Secure Channel Active</span>
                </div>
            </div>

            {/* Chat Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
                {chatHistory.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                        <MessageSquare className="w-12 h-12 text-slate-600" />
                        <p className="text-slate-500 text-sm italic">بانتظار تعليماتك السيادية...<br />(Awaiting your sovereign instructions...)</p>
                    </div>
                )}

                {chatHistory.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`
                            max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed
                            ${msg.role === 'user' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-slate-800 text-slate-200 border border-slate-700'}
                        `}>
                            {msg.role === 'agent' && (
                                <div className="text-[10px] font-mono text-indigo-400 mb-2 uppercase tracking-wider">{msg.agent}</div>
                            )}
                            {msg.content}

                            {msg.sentinel && (
                                <div className="mt-3 pt-3 border-t border-slate-700 flex items-start gap-2">
                                    <Shield className="w-3 h-3 text-emerald-500 mt-0.5" />
                                    <div className="text-[10px] text-slate-500 italic">Sentinel Insight: {msg.sentinel}</div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Action Queue */}
            {awaitingSign && (
                <div className="p-4 bg-indigo-500/5 border-t border-indigo-500/20 animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <Terminal className="text-indigo-400 w-5 h-5" />
                            <div className="text-xs">
                                <span className="text-slate-400 font-bold tracking-wider">{awaitingSign.id}:</span>
                                <span className="text-white ml-2">بانتظار توقيعك للتنفيذ... (Awaiting Signature)</span>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-bold transition-all">تجاهل</button>
                            <button
                                onClick={() => setAwaitingSign(null)}
                                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold flex items-center gap-2 transition-all shadow-lg shadow-indigo-600/20"
                            >
                                <CheckCircle2 className="w-4 h-4" /> توقيع وتنفيذ (Sign & Execute)
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Progress Bar (Latency Visualization) */}
            {isProcessing && (
                <div className="h-1 bg-slate-800 w-full overflow-hidden">
                    <div className="h-full bg-indigo-500 animate-[loading_2s_infinite]"></div>
                </div>
            )}

            {/* Footer Input */}
            <div className="p-4 bg-slate-900 border-t border-slate-800 flex gap-4">
                <input
                    className="flex-1 bg-slate-800 border border-slate-700 rounded-2xl px-6 py-4 text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all placeholder:text-slate-600"
                    placeholder="وجه تعليماتك للوكيل التنفيذي هنا..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                />
                <button
                    onClick={handleSend}
                    disabled={isProcessing}
                    className="w-14 h-14 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl flex items-center justify-center transition-all shadow-lg shadow-indigo-600/20"
                >
                    <Send className="w-6 h-6" />
                </button>
            </div>
        </div>
    );
}
