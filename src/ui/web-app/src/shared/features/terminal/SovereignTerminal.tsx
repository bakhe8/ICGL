import { FitAddon } from '@xterm/addon-fit';
import { Terminal } from '@xterm/xterm';
import '@xterm/xterm/css/xterm.css';
import { useEffect, useRef } from 'react';
import { resolveWsUrl } from '../../client';

interface SovereignTerminalProps {
    className?: string;
}

export function SovereignTerminal({ className }: SovereignTerminalProps) {
    const terminalRef = useRef<HTMLDivElement>(null);
    const termInstance = useRef<Terminal | null>(null);
    const wsInstance = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!terminalRef.current) return;

        // prevent double init
        if (termInstance.current) return;

        // Initialize xterm
        const term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#0F172A', // Slate-900 (matches "Sovereign" dark theme)
                foreground: '#E2E8F0', // Slate-200
                cursor: '#10B981',     // Emerald-500
            },
            fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            fontSize: 14,
            allowProposedApi: true,
        });

        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);

        term.open(terminalRef.current);
        fitAddon.fit();
        termInstance.current = term;

        // Connect WebSocket
        const wsUrl = resolveWsUrl('/api/chat/terminal/ws');

        term.writeln('\x1b[32mInitializing Sovereign Link...\x1b[0m');

        const ws = new WebSocket(wsUrl);
        wsInstance.current = ws;

        ws.onopen = () => {
            term.writeln('Connected to Sovereign Core [v5.0.0]');
            term.writeln('');
            term.writeln('\x1b[33mNote: Terminal is in read-only demo mode; commands are ignored.\x1b[0m');
            term.writeln('');
            // Send a ping or initial command if needed
        };

        ws.onmessage = (event) => {
            term.write(event.data);
        };

        ws.onerror = (e) => {
            console.error('WS Error', e);
            term.writeln('\r\n\x1b[31mConnection Error.\x1b[0m');
        };

        ws.onclose = () => {
            term.writeln('\r\n\x1b[33mConnection Closed (stub mode).\x1b[0m');
        };

        // User input
        term.onData((data) => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(data);
            }
        });

        // Resize observer
        const resizeObserver = new ResizeObserver(() => {
            fitAddon.fit();
        });
        resizeObserver.observe(terminalRef.current);

        return () => {
            resizeObserver.disconnect();
            ws.close();
            term.dispose();
            termInstance.current = null;
        };
    }, []);

    return (
        <div className={`w-full h-full bg-slate-950 p-2 rounded-lg border border-slate-800 shadow-inner ${className}`}>
            <div ref={terminalRef} className="w-full h-full overflow-hidden" />
        </div>
    );
}
