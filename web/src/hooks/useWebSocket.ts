import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * WebSocket Hook for SCP Real-Time Communication
 */

interface WebSocketMessage {
    type: string;
    data?: unknown;
    [key: string]: unknown;
}

interface UseWebSocketReturn {
    lastMessage: WebSocketMessage | null;
    sendMessage: (message: WebSocketMessage) => void;
    isConnected: boolean;
}

export function useWebSocket(url: string): UseWebSocketReturn {
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [reconnectCount, setReconnectCount] = useState(0);
    const ws = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<number | null>(null);

    const connect = useCallback(() => {
        try {
            ws.current = new WebSocket(url);

            ws.current.onopen = () => {
                console.log('✅ WebSocket connected');
                setIsConnected(true);

                // Send ping to keep alive
                const pingInterval = setInterval(() => {
                    if (ws.current?.readyState === WebSocket.OPEN) {
                        ws.current.send(JSON.stringify({ type: 'ping' }));
                    }
                }, 30000); // Every 30s

                if (ws.current) {
                    const currentWs = ws.current;
                    const originalOnClose = currentWs.onclose;
                    currentWs.onclose = (ev) => {
                        clearInterval(pingInterval);
                        if (originalOnClose) originalOnClose.call(currentWs, ev);
                    };
                }
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as WebSocketMessage;
                    if (data.type !== 'pong') { // Ignore pong responses
                        setLastMessage(data);
                    }
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.current.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
            };

            ws.current.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                setIsConnected(false);

                // Reconnect after 3 seconds by incrementing count
                reconnectTimeout.current = window.setTimeout(() => {
                    console.log('🔄 Reconnecting...');
                    setReconnectCount(c => c + 1);
                }, 3000);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }, [url]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (ws.current) {
                // Disable onclose to prevent auto-reconnect during unmount
                ws.current.onclose = null;
                ws.current.close();
            }
        };
    }, [connect, reconnectCount]);

    const sendMessage = useCallback((message: WebSocketMessage) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }, []);

    return { lastMessage, sendMessage, isConnected };
}
