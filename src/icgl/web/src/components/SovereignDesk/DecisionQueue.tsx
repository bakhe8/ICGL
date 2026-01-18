import { Vote } from 'lucide-react';


interface Decision {
    id: string;
    title: string;
    priority: 'high' | 'medium' | 'low';
    description?: string;
    status?: string;
}

interface DecisionQueueProps {
    decisions?: Decision[];
    onApprove?: (id: string) => void;
    onReject?: (id: string) => void;
    onDetails?: (id: string) => void;
    actioningId?: string | null;
}

export const DecisionQueue = ({ decisions, onApprove, onReject, onDetails, actioningId }: DecisionQueueProps) => {
    const allDecisions = decisions || [];
    const pendingItems = allDecisions.filter(d => d.status !== 'APPROVED' && d.status !== 'REJECTED');
    const processedItems = allDecisions.filter(d => d.status === 'APPROVED' || d.status === 'REJECTED');

    const priorityConfig = {
        high: {
            border: 'border-red-500',
            bg: 'bg-red-50',
            badge: 'bg-red-500'
        },
        medium: {
            border: 'border-orange-500',
            bg: 'bg-orange-50',
            badge: 'bg-orange-500'
        },
        low: {
            border: 'border-green-500',
            bg: 'bg-green-50',
            badge: 'bg-green-500'
        }
    };

    return (
        <div className="w-full space-y-12">
            {/* Pending Decisions Section */}
            <div>
                <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                    <Vote className="text-yellow-600" size={24} />
                    🗳️ في انتظار توقيعك
                    {pendingItems.length > 0 && (
                        <span className="bg-yellow-100 text-yellow-700 text-sm px-3 py-1 rounded-full ml-auto font-mono">
                            {pendingItems.length}
                        </span>
                    )}
                </h2>

                <div className="space-y-4">
                    {pendingItems.length === 0 && (
                        <p className="text-gray-400 italic text-center py-8">لا توجد قرارات معلقة. المكتب نظيف. ✨</p>
                    )}
                    {pendingItems.map((decision) => {
                        const config = priorityConfig[decision.priority];
                        return (
                            <div
                                key={decision.id}
                                className={`group relative bg-white border border-gray-100 rounded-2xl p-6 transition-all hover:shadow-md hover:border-blue-100/50 flex flex-col sm:flex-row gap-4 items-start sm:items-center`}
                            >
                                <div className={`absolute left-0 top-6 bottom-6 w-1 rounded-r-full ${config.bg.replace('bg-', 'bg-').replace('-50', '-500')}`}></div>

                                <div className="flex-1 pl-4">
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="font-bold text-gray-800 text-lg">{decision.title}</h3>
                                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${config.bg} ${config.badge.replace('bg-', 'text-')}`}>
                                            {decision.priority}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-400 font-medium">
                                        {decision.id} • في انتظار الموافقة النهائية
                                    </p>
                                </div>

                                <div className="flex gap-3 w-full sm:w-auto pl-4 sm:pl-0 border-t sm:border-0 border-gray-50 pt-4 sm:pt-0">
                                    <button
                                        onClick={() => onDetails?.(decision.id)}
                                        className="px-4 py-2 bg-gray-50 text-gray-600 rounded-xl text-sm font-bold hover:bg-gray-100 transition-colors"
                                    >
                                        تفاصيل
                                    </button>
                                    <button
                                        onClick={() => onReject?.(decision.id)}
                                        disabled={actioningId === decision.id}
                                        className="px-4 py-2 bg-white border border-red-100 text-red-600 rounded-xl text-sm font-bold hover:bg-red-50 transition-colors"
                                    >
                                        رفض
                                    </button>
                                    <button
                                        onClick={() => onApprove?.(decision.id)}
                                        disabled={actioningId === decision.id}
                                        className="px-6 py-2 bg-gray-900 text-white rounded-xl text-sm font-bold shadow-lg shadow-gray-200 hover:bg-black transition-all hover:-translate-y-0.5"
                                    >
                                        {actioningId === decision.id ? '...' : 'اعتماد'}
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Processed / Active Execution Section */}
            {processedItems.length > 0 && (
                <div className="pt-8 border-t border-gray-100">
                    <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                        <span className="text-green-600 text-2xl">⚡</span>
                        تنفيذ نشط (Active Execution)
                        <span className="bg-green-100 text-green-700 text-sm px-3 py-1 rounded-full ml-auto font-mono">
                            {processedItems.length}
                        </span>
                    </h2>

                    <div className="space-y-4 opacity-80 hover:opacity-100 transition-opacity">
                        {processedItems.map((decision) => (
                            <div
                                key={decision.id}
                                className="bg-gray-50/50 border border-gray-200 rounded-xl p-5 flex flex-col sm:flex-row gap-4 items-center"
                            >
                                <div className="text-2xl">
                                    {decision.status === 'APPROVED' ? '🚀' : '🛑'}
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-bold text-gray-700 decoration-gray-400">{decision.title}</h3>
                                    <p className="text-xs text-gray-400 font-mono uppercase tracking-wider">
                                        Status: {decision.status} • {decision.status === 'APPROVED' ? 'Executing' : 'Cancelled'}
                                    </p>
                                </div>
                                <button
                                    onClick={() => onDetails?.(decision.id)}
                                    className="px-4 py-2 bg-white border border-gray-200 text-gray-500 rounded-lg text-sm font-bold hover:bg-white hover:text-blue-600 hover:border-blue-200 transition-colors shadow-sm"
                                >
                                    عرض السجل
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
