import { FitAddon } from "@xterm/addon-fit";
import { Terminal } from "@xterm/xterm";
import "@xterm/xterm/css/xterm.css";
import React, { useEffect, useRef } from "react";

export interface SovereignTerminalProps {
  className?: string;
}

export const SovereignTerminal: React.FC<SovereignTerminalProps> = ({ className }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const termInstance = useRef<Terminal | null>(null);
  const wsInstance = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;
    if (termInstance.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: {
        background: "#0F172A",
        foreground: "#E2E8F0",
        cursor: "#10B981",
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

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/api/ws/terminal`;

    term.writeln("\x1b[32mInitializing Sovereign Link...\x1b[0m");

    const ws = new WebSocket(wsUrl);
    wsInstance.current = ws;

    ws.onopen = () => {
      term.writeln("Connected to Sovereign Core [v5.0.0]");
      term.writeln("");
      term.writeln("\x1b[33mNote: Terminal is in read-only demo mode; commands are ignored.\x1b[0m");
      term.writeln("");
    };

    ws.onmessage = (event) => {
      term.write(event.data);
    };

    ws.onerror = (e) => {
      console.error("WS Error", e);
      term.writeln("\r\n\x1b[31mConnection Error.\x1b[0m");
    };

    ws.onclose = () => {
      term.writeln("\r\n\x1b[33mConnection Closed (stub mode).\x1b[0m");
    };

    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

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
    <div className={`w-full h-full bg-slate-950 p-2 rounded-lg border border-slate-800 shadow-inner ${className || ""}`}>
      <div ref={terminalRef} className="w-full h-full overflow-hidden" />
    </div>
  );
};
