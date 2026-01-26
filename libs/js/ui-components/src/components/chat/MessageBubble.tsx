import React from "react";
import { AlertTriangle, Bot, ShieldCheck, User } from "lucide-react";

export type ChatBlock =
  | { type: "analysis" | "alerts" | "actions" | "text" | "metrics" | "memory" | "adr" | "adr_details" | "data"; title?: string; collapsed?: boolean; data: any };

export type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
  text?: string;
  blocks?: ChatBlock[];
  timestamp?: string;
};

export interface MessageBubbleProps {
  message: ChatMessage;
  onAction?: (action: string) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onAction }) => {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex gap-4 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-200">
        <AlertTriangle size={20} className="shrink-0 mt-1" />
        <div>{message.content}</div>
      </div>
    );
  }

  return (
    <div className={`flex gap-4 p-2 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? "bg-indigo-500" : "bg-emerald-600"}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`px-4 py-3 rounded-2xl glass-panel border-0 ${isUser ? "bg-indigo-500/20 text-white rounded-tr-sm" : "bg-white/5 text-white/90 rounded-tl-sm"}`}
        >
          <React.Fragment>{message.text || message.content}</React.Fragment>
        </div>

        {!isUser && message.blocks && message.blocks.length > 0 && (
          <div className="flex flex-col gap-2 w-full mt-1">
            {message.blocks.map((block, i) => (
              <BlockRenderer key={i} block={block} onAction={onAction} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const BlockRenderer = ({ block, onAction }: { block: ChatBlock; onAction?: (a: string) => void }) => {
  if (block.type === "alerts") {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-sm">
        <div className="flex items-center gap-2 text-red-300 font-medium mb-2">
          <ShieldAlertIcon />
          {block.title}
        </div>
        <ul className="list-disc pl-5 space-y-1 text-red-200/80">
          {block.data.alerts.map((a: { message: string } | string, i: number) => (
            <li key={i}>{typeof a === "string" ? a : a.message}</li>
          ))}
        </ul>
      </div>
    );
  }

  if (block.type === "actions") {
    return (
      <div className="flex gap-2 flex-wrap">
        {block.data.actions.map((act: { label: string; action: string; value?: string }, i: number) => (
          <button
            key={i}
            onClick={() => onAction && onAction(act.value || act.action)}
            className="px-3 py-1.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition-colors text-sm font-medium hover:scale-105 active:scale-95 transition-transform"
          >
            {act.label}
          </button>
        ))}
      </div>
    );
  }

  if (block.type === "text") {
    return (
      <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-sm">
        {block.title && <div className="font-medium text-white/70 mb-1">{block.title}</div>}
        <div className="text-white/80 whitespace-pre-wrap">{block.data.content}</div>
      </div>
    );
  }

  if (block.type === "metrics") {
    return (
      <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-sm">
        {block.title && <div className="font-medium text-white/70 mb-2">{block.title}</div>}
        <div className="grid grid-cols-2 gap-2 text-white/70 text-xs">
          {Object.entries(block.data).map(([key, value]) => (
            <div key={key} className="flex justify-between gap-2 bg-white/5 rounded px-2 py-1">
              <span className="text-white/50">{key}</span>
              <span className="text-white/80">{String(value)}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (block.type === "memory") {
    const matches = block.data.matches || [];
    return (
      <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-sm">
        {block.title && <div className="font-medium text-white/70 mb-2">{block.title}</div>}
        {matches.length === 0 ? (
          <div className="text-white/50 text-xs">No matches found.</div>
        ) : (
          <div className="space-y-2">
            {matches.map((m: { title?: string; id?: string; score?: number; snippet?: string }, i: number) => (
              <div key={i} className="rounded border border-white/10 bg-white/5 p-2">
                <div className="text-xs text-white/80">{m.title || m.id || "Memory"}</div>
                {typeof m.score === "number" && <div className="text-[10px] text-white/40">Score: {m.score}</div>}
                {m.snippet && <div className="text-xs text-white/60 mt-1">{m.snippet}</div>}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-sm">
      <div className="font-medium text-white/70 mb-1">{block.title}</div>
      <pre className="whitespace-pre-wrap text-white/50 text-xs font-mono">{JSON.stringify(block.data, null, 2)}</pre>
    </div>
  );
};

const ShieldAlertIcon = () => <ShieldCheck size={14} />;

export default MessageBubble;
