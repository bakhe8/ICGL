
import { Bot, Radio, Send, User } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { sendChatMessage } from '../../api/system';

interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    text: string;
    timestamp: string;
}


export const Chat = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Initial welcome message
    useEffect(() => {
        setMessages([
            {
                role: 'assistant',
                text: 'Coordination Hub (COC) Active. I can clarify agent logic and resolve dialogue deadlocks.',
                timestamp: new Date().toISOString()
            }
        ]);
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: ChatMessage = {
            role: 'user',
            text: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        // ... inside Chat ...

        try {
            const data = await sendChatMessage({
                message: input,
                actor: 'coordinator', // mapped from agent_id
                session_id: 'admin_coc'
            });

            // Handle response format from generic ChatResponse
            const responseText = data.text || (data.messages && data.messages.length > 0 ? data.messages[data.messages.length - 1].text : 'Coordination logic processed.');

            const assistantMsg: ChatMessage = {
                role: 'assistant',
                text: responseText || 'No response text.',
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error('Chat error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-50/50 rounded-2xl overflow-hidden border border-slate-100">
            <div className="p-4 border-b border-white bg-white/50 backdrop-blur-sm flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Radio className="w-4 h-4 text-indigo-500 animate-pulse" />
                    <span className="font-bold text-slate-800 text-sm italic">Coordination Engine (COC)</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-400 border border-slate-100'
                            }`}>
                            {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                        </div>
                        <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm shadow-sm border ${msg.role === 'user'
                            ? 'bg-indigo-600 text-white border-indigo-700 rounded-tr-sm'
                            : 'bg-white text-slate-700 border-slate-100 rounded-tl-sm'
                            }`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-2 p-2 items-center text-slate-400 text-[10px] animate-pulse">
                        <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" />
                        <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0.2s]" />
                        <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0.4s]" />
                        <span>Solving Logic...</span>
                    </div>
                )}
            </div>

            <div className="p-4 bg-white border-t border-slate-50">
                <div className="flex gap-2">
                    <input
                        className="flex-1 bg-slate-100 border-none rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
                        placeholder="Request coordination help..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSend()}
                    />
                    <button
                        onClick={handleSend}
                        className="p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Chat;
