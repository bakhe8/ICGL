import { useEffect, useRef, useState } from 'react';
import { resolveWsUrl } from '../client';

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
        // Use resolveWsUrl to handle proxy/production correctly
        const wsUrl = resolveWsUrl('/api/system/live');

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
