import { useState } from 'react';
import type { ChatMessage } from '@web-src/api/types';
import { useMutation } from '@tanstack/react-query';
import { sendChatMessage } from '@web-src/api/queries';

interface AgentChatProps {
    agentId: string;
}

export function AgentChat({ agentId }: AgentChatProps) {
    const [chatInput, setChatInput] = useState('');
    const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
    const [chatSession, setChatSession] = useState<string | undefined>(undefined);
    const [autoExecute] = useState(true);

    const chatMutation = useMutation({
        mutationKey: ['chat', agentId],
        mutationFn: async () => {
            if (!chatInput.trim()) throw new Error('اكتب رسالة');
            const res = await sendChatMessage({
                message: chatInput.trim(),
                session_id: chatSession,
                actor: agentId,
                auto_execute: autoExecute,
            });
            return res;
        },
        onSuccess: (res) => {
            setChatSession((prev) => prev || (res.state?.session_id as string | undefined));
            setChatHistory((prev) => [...prev, ...res.messages]);
            setChatInput('');
        },
    });

    return (
        <div className="space-y-2 text-xs p-3 rounded-xl border border-slate-200 bg-white/80">
            <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 text-sm">استشارة خبير مباشر | Expert Consultation</span>
                {chatSession && <span className="text-slate-500 text-[11px]">Session: {chatSession}</span>}
            </div>
                <p className="text-[10px] text-slate-500 italic mb-2">هذه الجلسة مخصصة للاستفسار من الوكيل المختار فقط. البيانات هنا لا تغير المشروع بشكل مباشر.</p>
            <div className="flex gap-2">
                <textarea
                    className="flex-1 rounded border border-slate-300 px-2 py-1 text-sm bg-white text-slate-800"
                    placeholder="اكتب رسالتك للنموذج..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                />
                <button
                    className="px-3 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700 transition"
                    onClick={() => chatMutation.mutate()}
                    disabled={chatMutation.isPending}
                >
                    {chatMutation.isPending ? '...' : 'إرسال'}
                </button>
            </div>
            <div className="space-y-1 max-h-48 overflow-y-auto">
                {chatHistory.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`p-2 rounded border text-[12px] ${msg.role === 'user'
                            ? 'bg-slate-100 border-slate-200 text-slate-800'
                            : msg.role === 'assistant'
                                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                                : 'bg-slate-50 border-slate-200 text-slate-600'
                            }`}
                    >
                        <div className="text-[11px] text-slate-500 font-bold mb-1">{msg.role}</div>
                        <div className="whitespace-pre-wrap leading-relaxed">{msg.text || msg.content}</div>
                    </div>
                ))}
                {chatHistory.length === 0 && <div className="text-slate-500 text-[11px]">لا يوجد محادثات بعد</div>}
            </div>
        </div>
    );
}
