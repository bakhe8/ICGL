
import { useEffect, useState } from 'react';
import { ChatConsole, type ChatMessage } from '@icgl/ui-components';

export const Chat = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setMessages([
            {
                role: 'assistant',
                content: 'Coordination Hub (COC) Active. I can clarify agent logic and resolve dialogue deadlocks.',
                timestamp: new Date().toISOString(),
            },
        ]);
    }, []);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: ChatMessage = {
            role: 'user',
            content: input,
            text: input,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const baseUrl = 'http://127.0.0.1:8000';
            const res = await fetch(`${baseUrl}/api/agent/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    agent_id: 'coordinator',
                    session_id: 'admin_coc',
                }),
            });

            const data = await res.json();
            const assistantMsg: ChatMessage = {
                role: 'assistant',
                content: data.text || 'Coordination logic processed.',
                text: data.text || 'Coordination logic processed.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } catch (error) {
            console.error('Chat error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <ChatConsole
            messages={messages}
            inputValue={input}
            loading={loading}
            onInputChange={setInput}
            onSend={handleSend}
            title="Coordination Engine (COC)"
        />
    );
};

export default Chat;
