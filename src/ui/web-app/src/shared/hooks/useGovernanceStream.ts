import { useEffect, useRef, useState } from 'react';

export type StreamEvent = {
    type: 'log' | 'proposal_update' | 'agent_status' | 'system_pulse';
    payload: any;
    timestamp: string;
};

export function useGovernanceStream() {
    const [events, setEvents] = useState<StreamEvent[]>([]);
    const [status, setStatus] = useState<'CONNECTING' | 'CONNECTED' | 'DISCONNECTED'>('DISCONNECTED');
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<any>(null);

    const connect = () => {
        // Use relative path for production compatibility, assuming proxy
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host; // e.g. localhost:3000 or production domain
        // If we are on dev (port 3000) and backend is 8000, we might need explicit handling or proxy
        // Ideally the vite proxy handles /api requests to backend
        // Standard convention for this project has been explicit /api prefixes.
        // We'll try to connect to the same host but upgrade to WS, relying on proxy.
        // If that fails, we might need a distinct WS_URL config.

        // For now, hardcoding the backend port if on localhost to match queries.ts behavior logic (implied via proxy)
        // But since we removed hardcoded URLs, we should use window.location with /api/ws prefix?
        // Let's assume /api/system/live endpoint for WS.

        const wsUrl = `${protocol}//${host}/api/system/live`;

        // Fallback for direct backend dev if needed (often frontend 3000, backend 8000)
        // const wsUrl = 'ws://localhost:8000/api/system/live'; 

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Governance Stream Connected');
            setStatus('CONNECTED');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const streamEvent: StreamEvent = {
                    type: data.type || 'system_pulse',
                    payload: data.payload || data,
                    timestamp: new Date().toISOString()
                };

                setEvents(prev => [streamEvent, ...prev].slice(0, 50)); // Keep last 50
            } catch (e) {
                console.error('Stream parse error', e);
            }
        };

        ws.onclose = () => {
            console.log('Governance Stream Disconnected');
            setStatus('DISCONNECTED');
            // Reconnect logic
            reconnectTimeoutRef.current = setTimeout(connect, 3000);
        };

        ws.onerror = (err) => {
            console.error('Governance Stream Error', err);
            ws.close();
        };

        wsRef.current = ws;
    };

    useEffect(() => {
        connect();
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        };
    }, []);

    return {
        events,
        status,
        latestEvent: events[0]
    };
}
