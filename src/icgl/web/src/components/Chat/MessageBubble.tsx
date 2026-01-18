import { User, Bot, AlertTriangle, ShieldCheck, BarChart3, Brain } from 'lucide-react';

// --- Types (Kept same for compatibility) ---
interface BaseBlock {
    title?: string;
    collapsed?: boolean;
}

export type ChatBlock =
    | (BaseBlock & { type: 'analysis'; data: Record<string, unknown> })
    | (BaseBlock & { type: 'alerts'; data: { alerts: (string | { message: string })[] } })
    | (BaseBlock & { type: 'actions'; data: { actions: { label: string; action: string; value?: string }[] } })
    | (BaseBlock & { type: 'text'; data: { content: string } })
    | (BaseBlock & { type: 'metrics'; data: Record<string, unknown> })
    | (BaseBlock & { type: 'memory'; data: { matches?: Array<{ id?: string; title?: string; score?: number; snippet?: string }> } })
    | (BaseBlock & { type: 'adr' | 'adr_details' | 'data'; data: Record<string, unknown> });

export interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    text?: string;
    blocks?: ChatBlock[];
}

interface MessageBubbleProps {
    message: Message;
    onAction?: (action: string) => void;
}

// --- Main Component ---
export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onAction }) => {
    const isUser = message.role === 'user';
    const isSystem = message.role === 'system';

    // System Message
    if (isSystem) {
        return (
            <div className="flex gap-3 mx-auto max-w-2xl w-full p-4 rounded-lg bg-orange-50 border border-orange-200 text-orange-800 my-2" role="alert">
                <AlertTriangle size={20} className="shrink-0 mt-0.5 text-orange-600" aria-hidden="true" />
                <div className="text-sm font-medium">{message.content}</div>
            </div>
        );
    }

    // User/Assistant Message
    return (
        <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} group`}>
            {/* Avatar */}
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm border ${isUser
                ? 'bg-blue-600 border-blue-700 text-white'
                : 'bg-white border-gray-200 text-purple-600'
                }`} aria-hidden="true">
                {isUser ? <User size={18} /> : <Bot size={18} />}
            </div>

            {/* Bubble Container */}
            <div className={`flex flex-col gap-2 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>

                {/* Text Content */}
                {(message.text || message.content) && (
                    <div className={`px-5 py-3.5 shadow-sm text-sm leading-relaxed ${isUser
                        ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm'
                        : 'bg-white border border-gray-200 text-gray-800 rounded-2xl rounded-tl-sm'
                        }`}>
                        <div className="whitespace-pre-wrap font-medium">
                            {message.text || message.content}
                        </div>
                    </div>
                )}

                {/* Blocks (Assistant Only) */}
                {!isUser && message.blocks && message.blocks.length > 0 && (
                    <div className="flex flex-col gap-3 w-full min-w-[300px] mt-1">
                        {message.blocks.map((block, i) => (
                            <BlockRenderer key={i} block={block} onAction={onAction} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

// --- Block Renderers (Rebuilt for Light Theme) ---

const BlockRenderer = ({ block, onAction }: { block: ChatBlock; onAction?: (a: string) => void }) => {

    // 1. Alerts Block
    if (block.type === 'alerts') {
        return (
            <div className="bg-red-50 border border-red-100 rounded-lg p-4 shadow-sm" role="alert" aria-live="polite">
                <div className="flex items-center gap-2 text-red-700 font-bold mb-3 text-sm border-b border-red-100 pb-2">
                    <ShieldCheck size={16} aria-hidden="true" />
                    {block.title || 'تنبيات النظام'}
                </div>
                <ul className="space-y-2">
                    {block.data.alerts.map((a: any, i: number) => (
                        <li key={i} className="flex gap-2 text-sm text-red-800 bg-red-100/50 p-2 rounded">
                            <span className="text-red-500" aria-hidden="true">•</span>
                            {typeof a === 'string' ? a : a.message}
                        </li>
                    ))}
                </ul>
            </div>
        );
    }

    // 2. Metrics Block
    if (block.type === 'metrics') {
        return (
            <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 text-gray-700 font-bold mb-3 text-sm">
                    <BarChart3 size={16} aria-hidden="true" />
                    {block.title || 'تحليل البيانات'}
                </div>
                <div className="grid grid-cols-2 gap-3">
                    {Object.entries(block.data).map(([key, value], i) => (
                        <div key={i} className="bg-gray-50 p-2 rounded border border-gray-100">
                            <div className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</div>
                            <div className="font-mono font-bold text-gray-800">{String(value)}</div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // 3. Analysis Block (Generic)
    if (block.type === 'analysis') {
        return (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 shadow-sm">
                <div className="flex items-center gap-2 text-blue-800 font-bold mb-2 text-sm">
                    <Brain size={16} aria-hidden="true" />
                    {block.title || 'تحليل ذكي'}
                </div>
                {/* Render key-values decently */}
                <div className="space-y-1">
                    {Object.entries(block.data).map(([k, v], i) => (
                        <div key={i} className="flex justify-between text-sm text-blue-900/80 border-b border-blue-100/50 last:border-0 py-1">
                            <span className="capitalize opacity-75">{k}:</span>
                            <span className="font-semibold">{String(v)}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // 4. Actions Block
    if (block.type === 'actions') {
        return (
            <div className="flex flex-wrap gap-2 mt-1" role="group" aria-label="الإجراءات المتاحة">
                {block.data.actions.map((act, i) => (
                    <button
                        key={i}
                        onClick={() => onAction && onAction(act.action)}
                        className="px-3 py-1.5 bg-white border border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300 rounded-lg text-xs font-bold shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500"
                        title={act.label}
                    >
                        {act.label}
                    </button>
                ))}
            </div>
        );
    }

    return null;
};
