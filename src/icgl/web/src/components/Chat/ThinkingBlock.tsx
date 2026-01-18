import { Loader2 } from 'lucide-react';

export const ThinkingBlock = () => {
    return (
        <div className="flex gap-4 p-2 animate-in fade-in duration-300">
            {/* Avatar */}
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center shrink-0 border border-blue-100">
                <Loader2 size={16} className="animate-spin text-blue-600" />
            </div>

            {/* Content */}
            <div className="flex flex-col gap-1 py-1">
                <span className="text-sm font-semibold text-gray-700">جاري التفكير...</span>
                <span className="text-xs text-gray-500">يقوم المستشار الذكي بتحليل البيانات والتأكد من السياسات</span>
            </div>
        </div>
    );
};
