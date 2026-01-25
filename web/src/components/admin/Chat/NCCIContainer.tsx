
import { Send, Sparkles, Wifi, WifiOff } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useChat } from '../../../hooks/admin/useChat';
import { MessageBubble } from './MessageBubble';
import { ThinkingBlock } from './ThinkingBlock';

export const NCCIContainer = () => {
    const wsUrl = typeof window !== 'undefined'
        ? `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/chat`
        : 'ws://127.0.0.1:8000/ws/chat';
    const { messages, thinking, sendMessage, status, state } = useChat(wsUrl);
    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, thinking]);

    const handleSend = () => {
        if (!input.trim()) return;
        sendMessage(input);
        setInput('');
    };

    const handleAction = (action: string) => {
        // Send the action directly as a message
        // E.g. "APPROVE" or "REJECT" or "submit_signature" if value not present
        sendMessage(action.toUpperCase(), { silent: true });
    };

    const awaitingSignature = Boolean(state && (state as { waiting_for_human?: boolean }).waiting_for_human);
    const pendingAdrId = state && (state as { adr_id?: string }).adr_id ? String((state as { adr_id?: string }).adr_id) : undefined;


    return (
        <div className="flex flex-col h-full max-h-[calc(100vh-8rem)]">
            {/* Connection Status Indicator */}
            <div className="absolute top-4 right-8 flex items-center gap-2 text-xs font-mono opacity-50">
                {status === 'connected' ? <Wifi size={12} className="text-emerald-500" /> : <WifiOff size={12} className="text-red-500" />}
                <span>{status.toUpperCase()}</span>
            </div>

            {/* Message List */}
            <div className="flex-1 overflow-y-auto pr-4 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent" ref={scrollRef}>
                {messages.map((m, i) => (
                    <MessageBubble key={i} message={m} onAction={handleAction} />
                ))}
                {thinking && <ThinkingBlock />}
            </div>

            {/* Input Area */}
            <div className="mt-6">
                {awaitingSignature && (
                    <div className="mb-3 flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-100">
                        <div>
                            Approval required{pendingAdrId ? ` for ${pendingAdrId}` : ''}.
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => handleAction('APPROVE')}
                                className="px-3 py-1.5 rounded-md bg-emerald-500/30 text-emerald-100 border border-emerald-400/40 hover:bg-emerald-500/40 transition-colors text-xs font-semibold"
                            >
                                Approve
                            </button>
                            <button
                                onClick={() => handleAction('REJECT')}
                                className="px-3 py-1.5 rounded-md bg-red-500/20 text-red-200 border border-red-400/40 hover:bg-red-500/30 transition-colors text-xs font-semibold"
                            >
                                Reject
                            </button>
                        </div>
                    </div>
                )}
                <div className={`glass-panel p-2 flex items-center gap-2 relative group focus-within:ring-1 focus-within:ring-purple-500/50 transition-all ${status !== 'connected' ? 'opacity-50 pointer-events-none' : ''}`}>
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={status === 'connected' ? "Direct Governance Command | أصدر أمراً برمجياً سيادياً" : "Connecting to Neural Core..."}
                        className="flex-1 bg-transparent border-none outline-none text-white placeholder-white/20 px-4 py-2 font-medium"
                    />
                    <button
                        onClick={handleSend}
                        title="Send Command"
                        aria-label="Send Command"
                        className="p-2 rounded-md bg-purple-600 hover:bg-purple-500 text-white transition-colors shadow-lg shadow-purple-600/20 disabled:opacity-50"
                        disabled={status !== 'connected'}
                    >
                        <Send size={18} />
                    </button>

                    {/* Ambient Glow */}
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-focus-within:opacity-100 pointer-events-none transition-opacity" />
                </div>
                <div className="mt-2 flex items-center gap-2 text-xs text-white/30 px-2">
                    <Sparkles size={12} />
                    <span>Neural Core Command Interface (NCCI) | واجهة التحكم في النواة العصبية</span>
                </div>
            </div>
        </div>
    );
};

export default NCCIContainer;
