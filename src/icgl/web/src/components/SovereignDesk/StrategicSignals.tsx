import { Radio, Eye, Clock } from 'lucide-react';


interface Signal {
    id: string;
    icon: string;
    title: string;
    type: 'warning' | 'info' | 'suggestion';
}

interface StrategicSignalsProps {
    signals?: Signal[];
    onView?: (id: string) => void;
    onDelegate?: (id: string) => void;
}

export const StrategicSignals = ({ signals, onView, onDelegate }: StrategicSignalsProps) => {
    const defaultSignals: Signal[] = [
        { id: '1', icon: '⚠️', title: '6 سياسات مفقودة', type: 'warning' },
        { id: '2', icon: '💡', title: 'توصية: تفعيل GitOps', type: 'suggestion' },
        { id: '3', icon: '📊', title: 'تقرير أداء جديد', type: 'info' }
    ];

    const items = signals && signals.length > 0 ? signals : defaultSignals;

    const typeConfig = {
        warning: {
            bg: 'bg-orange-50',
            border: 'border-orange-200',
            text: 'text-orange-800'
        },
        info: {
            bg: 'bg-blue-50',
            border: 'border-blue-200',
            text: 'text-blue-800'
        },
        suggestion: {
            bg: 'bg-purple-50',
            border: 'border-purple-200',
            text: 'text-purple-800'
        }
    };

    return (
        <div className="w-full">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Radio className="text-blue-600" size={24} />
                📡 إشارات تحتاج انتباهك
            </h2>

            <div className="space-y-3 max-h-96 overflow-y-auto">
                {items.map((signal) => {
                    const config = typeConfig[signal.type];
                    return (
                        <div
                            key={signal.id}
                            className={`${config.bg} ${config.border} border-2 p-4 rounded-lg transition-all hover:shadow-md`}
                        >
                            <div className="flex items-start gap-3">
                                <span className="text-2xl">{signal.icon}</span>
                                <div className="flex-1">
                                    <p className={`font-semibold ${config.text}`}>{signal.title}</p>
                                </div>
                            </div>

                            <div className="flex gap-2 mt-3">
                                <button
                                    onClick={() => onView?.(signal.id)}
                                    className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors flex items-center gap-1 font-semibold"
                                >
                                    <Eye size={14} />
                                    عرض
                                </button>
                                {signal.type === 'warning' && (
                                    <button
                                        onClick={() => onDelegate?.(signal.id)}
                                        className="px-3 py-1.5 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors flex items-center gap-1 font-semibold"
                                    >
                                        <Clock size={14} />
                                        تفويض
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {items.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                    <Radio size={48} className="mx-auto mb-2 opacity-30" />
                    <p>لا توجد إشارات حالياً</p>
                </div>
            )}
        </div>
    );
};
