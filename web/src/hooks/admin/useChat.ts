import { useEffect, useRef, useState } from 'react';
import { ChatBlock, Message } from '../../components/admin/Chat/MessageBubble';

interface ChatState {
    messages: Message[];
    status: 'connecting' | 'connected' | 'disconnected';
    thinking: boolean;
    state: Record<string, unknown> | null;
    sendMessage: (content: string, options?: { silent?: boolean }) => void;
}

export const useChat = (url: string): ChatState => {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'ICGL System Online. Connecting to core...' }
    ]);
    const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
    const [thinking, setThinking] = useState(false);
    const [state, setState] = useState<Record<string, unknown> | null>(null);

    // Use a ref for the socket to avoid re-renders or dependency cycles
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        let ws: WebSocket | null = null;
        try {
            ws = new WebSocket(url);
            socketRef.current = ws;

            ws.onopen = () => {
                setStatus('connected');
                setMessages(prev => [
                    ...prev,
                    { role: 'assistant', content: 'Secure connection established. Ready for directives.' }
                ]);
            };

            ws.onclose = () => {
                setStatus('disconnected');
            };

            ws.onerror = (err) => {
                console.error('WebSocket Error:', err);
                setStatus('disconnected');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'stream') {
                        if (!data.content) {
                            setThinking(true);
                            return;
                        }

                        setThinking(false);
                        setMessages(prev => {
                            const last = prev[prev.length - 1];
                            if (last && last.role === 'assistant' && !last.blocks) {
                                return [
                                    ...prev.slice(0, -1),
                                    { ...last, content: last.content + data.content, text: (last.text || '') + data.content }
                                ];
                            }
                            return [...prev, { role: 'assistant', content: data.content, text: data.content }];
                        });
                    }

                    if (data.type === 'block') {
                        setThinking(false);
                        setMessages(prev => {
                            const last = prev[prev.length - 1];
                            const blockData = data.content as any;
                            const newBlock: ChatBlock = {
                                type: data.block_type as ChatBlock['type'],
                                title: data.title,
                                data: blockData
                            };

                            if (last && last.role === 'assistant') {
                                return [
                                    ...prev.slice(0, -1),
                                    { ...last, blocks: [...(last.blocks || []), newBlock] }
                                ];
                            }
                            return [...prev, { role: 'assistant', content: '', blocks: [newBlock] }];
                        });
                    }

                    if (data.type === 'state') {
                        setState(data.state || null);
                    }
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };
        } catch (e) {
            console.error('Connection failed:', e);
            setTimeout(() => setStatus('disconnected'), 0);
        }

        return () => {
            if (ws) ws.close();
        };
    }, [url]);

    const sendMessage = (content: string, options?: { silent?: boolean }) => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            setThinking(true);
            if (!options?.silent) {
                setMessages(prev => [...prev, { role: 'user', content }]);
            }
            socketRef.current.send(JSON.stringify({
                type: 'message',
                content: content
            }));
        } else {
            console.error('Socket not connected');
        }
    };

    return { messages, status, thinking, state, sendMessage };
};
