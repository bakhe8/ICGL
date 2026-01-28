import type { Telemetry } from '../domains/tower/types';

export interface DocNode {
    name: string;
    path: string;
    type: 'directory' | 'file';
    size?: number;
    modified?: string;
    children?: DocNode[];
}

export interface DocsTreeResponse {
    roots: DocNode[];
}

export interface DocContentResponse {
    path: string;
    mime: string;
    content: string;
}

export interface SystemHealth {
    integrity_score: number;
    status: string;
    active_agents: number;
    active_operations: number;
    waiting_for_human?: boolean;
}

export interface SystemStatus {
    mode: string;
    waiting_for_human: boolean;
    active_alert_level: 'NONE' | 'HIGH' | 'CRITICAL';
    last_adr_id: string | null;
    telemetry: Telemetry;
}

export interface ChatMessage {
    role: 'user' | 'system' | 'assistant';
    content: string;
    text?: string;
    blocks?: unknown[];
    timestamp?: string;
}

export interface ToolCall {
    cmd: string;
    path?: string;
    content?: string;
    status?: string;
    output?: string;
    proposed?: ToolCall;
}

export interface ChatResponse {
    messages: ChatMessage[];
    state: Record<string, unknown>;
    suggestions: string[];
    executed?: ToolCall[];
    blocked_commands?: ToolCall[];
    commands?: ToolCall[];
    text?: string;
    intent?: string;
}

export interface AIFileEntry {
    path: string;
    size: number;
}

export interface AITerminalResponse {
    output: string;
}
