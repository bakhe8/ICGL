import { useState, useEffect, useRef } from 'react';
import './Chat.css';

/**
 * COC Chat Interface
 * 
 * Natural language conversation with ICGL.
 */

interface Message {
    message_id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

interface ChatResponse {
    session_id: string;
    response: string;
    dialogue_state: string;
    needs_clarification: boolean;
    pending_approval: {
        intent: string;
        risk_level: string;
    } | null;
    result?: Record<string, unknown>;
}

export function Chat() {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [dialogueState, setDialogueState] = useState('greeting');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Create session on mount
    useEffect(() => {
        createSession();
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const createSession = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/coc/sessions?user_id=web_user', {
                method: 'POST'
            });
            const data = await res.json();
            setSessionId(data.session_id);
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || !sessionId) return;

        const userMessage: Message = {
            message_id: `msg_${Date.now()}`,
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('http://127.0.0.1:8000/coc/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    message: input,
                    session_id: sessionId,
                    user_id: 'web_user'
                })
            });

            const data: ChatResponse = await res.json();

            const assistantMessage: Message = {
                message_id: `msg_${Date.now()}`,
                role: 'assistant',
                content: data.response,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, assistantMessage]);
            setDialogueState(data.dialogue_state);

        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage: Message = {
                message_id: `msg_${Date.now()}`,
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <div className="header-content">
                    <h2>💬 ICGL Chat</h2>
                    <div className="session-info">
                        <span className="dialogue-state">{dialogueState}</span>
                        {sessionId && <span className="session-id">{sessionId.slice(0, 16)}...</span>}
                    </div>
                </div>
            </div>

            <div className="chat-messages">
                {messages.length === 0 && (
                    <div className="welcome-message">
                        <h3>👋 Welcome to ICGL!</h3>
                        <p>I can help you with:</p>
                        <ul>
                            <li>🔗 Creating collaboration channels</li>
                            <li>📋 Managing governance policies</li>
                            <li>🔍 Analyzing your codebase</li>
                            <li>📚 Querying the knowledge base</li>
                        </ul>
                        <p className="hint">Try: "Create a channel between architect and security"</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div
                        key={msg.message_id}
                        className={`message ${msg.role}`}
                    >
                        <div className="message-bubble">
                            <div className="message-content">{msg.content}</div>
                            <div className="message-time">{formatTime(msg.timestamp)}</div>
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message assistant">
                        <div className="message-bubble typing">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
                <textarea
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    rows={1}
                    disabled={!sessionId || loading}
                />
                <button
                    className="send-button"
                    onClick={sendMessage}
                    disabled={!input.trim() || !sessionId || loading}
                >
                    {loading ? '⏳' : '📤'}
                </button>
            </div>
        </div>
    );
}

export default Chat;
