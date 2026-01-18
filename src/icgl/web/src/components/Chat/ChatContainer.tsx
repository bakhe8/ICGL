import { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { MessageBubble } from './MessageBubble';
import { ThinkingBlock } from './ThinkingBlock';

export const ChatContainer = () => {
    const wsUrl = typeof window !== 'undefined'
        ? `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/chat`
        : 'ws://127.0.0.1:8000/ws/chat';

    // Using existing hook for logic to maintain functionality
    const { messages, thinking, sendMessage, status, state } = useChat(wsUrl);

    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll logic
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
        sendMessage(action.toUpperCase(), { silent: true });
    };

    // Extract state for pending signatures
    const awaitingSignature = Boolean(state && (state as { waiting_for_human?: boolean }).waiting_for_human);
    const pendingAdrId = state && (state as { adr_id?: string }).adr_id ? String((state as { adr_id?: string }).adr_id) : undefined;

    return (
        <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* 1. Header Section */}
            <div className="bg-gray-50 border-b border-gray-200 p-4 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700">
                        <Sparkles size={18} />
                    </div>
                    <div>
                        <h2 className="font-bold text-gray-800 text-sm">المساعد التنفيذي</h2>
                        <span className="text-xs text-gray-500">Executive AI Assistant</span>
                    </div>
                </div>

                {/* Status Indicator */}
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${status === 'connected'
                    ? 'bg-green-50 text-green-700 border-green-200'
                    : 'bg-red-50 text-red-700 border-red-200'
                    }`}>
                    {status === 'connected' ? <Wifi size={12} /> : <WifiOff size={12} />}
                    <span>{status === 'connected' ? 'ONLINE' : 'OFFLINE'}</span>
                </div>
            </div>

            {/* 2. Messages Area */}
            <div
                className="flex-1 overflow-y-auto p-6 space-y-6 bg-white scrollbar-thin scrollbar-thumb-gray-200"
                ref={scrollRef}
            >
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-gray-400 opacity-60">
                        <Sparkles size={48} className="mb-4 text-gray-200" />
                        <p>جاهز لتلقي الأوامر، سيدي الرئيس</p>
                    </div>
                )}

                {messages.map((m, i) => (
                    <MessageBubble key={i} message={m} onAction={handleAction} />
                ))}

                {thinking && <ThinkingBlock />}
            </div>

            {/* 3. Action & Input Area */}
            <div className="bg-gray-50 border-t border-gray-200 p-4">
                {/* Pending Action Banner */}
                {awaitingSignature && (
                    <div className="mb-4 bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-center justify-between animate-pulse-slow">
                        <div className="flex items-center gap-2 text-amber-800">
                            <AlertTriangle size={16} />
                            <span className="text-sm font-medium">
                                مطلوب توقيعك على: {pendingAdrId || 'وثيقة إدارية'}
                            </span>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => handleAction('APPROVE')}
                                className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-bold rounded shadow-sm transition-colors"
                            >
                                موافق ✅
                            </button>
                            <button
                                onClick={() => handleAction('REJECT')}
                                className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded shadow-sm transition-colors"
                            >
                                رفض ❌
                            </button>
                        </div>
                    </div>
                )}

                {/* Input Field */}
                <div className="flex gap-3 relative">
                    <div className={`flex items-center gap-2 relative transition-all ${status !== 'connected' ? 'opacity-50 pointer-events-none' : ''}`}>
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder={status === 'connected' ? "أدخل أوامرك هنا..." : "جاري الاتصال..."}
                            className="flex-1 bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm transition-shadow"
                            dir="auto"
                            aria-label="رسالة المحادثة"
                        />
                        <button
                            onClick={handleSend}
                            title="إرسال الرسالة"
                            aria-label="إرسال الرسالة"
                            className="p-3 rounded-lg bg-blue-700 hover:bg-blue-800 text-white transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:bg-gray-400"
                            disabled={status !== 'connected' || !input.trim()}
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </div>

                <div className="text-center mt-2">
                    <span className="text-[10px] text-gray-400 uppercase tracking-widest font-medium">
                        Secure Governance Channel v2.0
                    </span>
                </div>
            </div>
        </div>
    );
};
