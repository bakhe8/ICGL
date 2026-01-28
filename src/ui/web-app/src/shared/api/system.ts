import type { AgentRegistryEntry } from '../../domains/hall/types';
import { fetchJson, postJson } from '../client';
import type { AITerminalResponse, ChatResponse, DocNode, SystemHealth, SystemStatus } from '../types';

export const fetchSystemHealth = () => fetchJson<SystemHealth>('/api/system/health');
export const fetchSystemStatus = () => fetchJson<SystemStatus>('/api/system/status');
export const fetchDashboardQuick = () => fetchJson<Record<string, unknown>>('/api/system/observability/stats');

// Chat
export const sendFreeChatMessage = (payload: { message: string; session_id?: string; paths?: string[]; extra_context?: string; auto_execute?: boolean; actor?: string }) =>
    postJson<ChatResponse>('/chat', payload);

export const sendChatMessage = (payload: { message: string; session_id?: string; actor?: string; auto_execute?: boolean }) =>
    postJson<ChatResponse>('/chat', payload);

export const runAITerminal = (payload: { cmd: string; path?: string; lines?: number; content?: string }) =>
    postJson<AITerminalResponse>('/api/chat/terminal', payload);

export const writeAIFile = (payload: { path: string; content: string; mode?: 'w' | 'a' }) =>
    postJson<{ status: string; file?: string; path?: string; message?: string }>('/api/chat/file/write', payload);

// Docs
export const fetchDocsTree = () => fetchJson<{ roots: DocNode[] }>('/api/system/docs/tree');
export const fetchDocContent = (path: string) =>
    fetchJson<{ path: string; content: string; mime: string }>(`/api/system/docs/content?path=${encodeURIComponent(path)}`);
export const listAIWorkspace = (path = '.', limit = 200) =>
    fetchJson<{ files: { path: string; type: string; size?: number; modified?: string }[]; status: string }>(
        `/api/workspace?path=${encodeURIComponent(path)}&limit=${limit}`,
    );
export const readAIFile = (path: string) =>
    fetchJson<{ path: string; content: string; size?: number }>(`/api/workspace/read?path=${encodeURIComponent(path)}`);
export const saveDocContent = (payload: { path: string; content: string }) =>
    postJson<{ status: string; path: string }>('/api/system/docs/save', payload);

export const fetchAgentsRegistry = () => fetchJson<{ agents: AgentRegistryEntry[] }>('/api/system/agents');
