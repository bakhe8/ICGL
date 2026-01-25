
import { Loader2 } from 'lucide-react';

export const ThinkingBlock = () => {
    return (
        <div className="flex gap-4 p-2 animate-enter">
            <div className="w-8 h-8 rounded-full bg-emerald-600/50 flex items-center justify-center shrink-0">
                <Loader2 size={16} className="animate-spin text-white/80" />
            </div>
            <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-emerald-400">Agentic Core Thinking...</span>
                <span className="text-xs text-white/40">Analyzing constraints and checking policies</span>
            </div>
        </div>
    );
};
