import { Heart, CheckCircle, AlertTriangle } from 'lucide-react';


interface HealthPulseProps {
    status?: {
        healthy: boolean;
        activeAgents: number;
        activeOperations: number;
    };
    onDetails?: () => void;
}

export const HealthPulse = ({ status, onDetails }: HealthPulseProps) => {
    const defaultStatus = {
        healthy: true,
        activeAgents: 12,
        activeOperations: 5
    };

    const data = status || defaultStatus;

    // Use passed handler, or fallback to internal logic (though parent should handle it)
    const handleClick = () => {
        if (onDetails) {
            onDetails();
        } else {
            console.log('No onDetails handler provided');
        }
    };

    return (
        <div className="w-full">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Heart className="text-red-500" size={24} />
                ❤️ نبض المنظومة
            </h2>

            <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                    <span className="text-gray-600 font-medium">الحالة</span>
                    <span className={`font-bold flex items-center gap-1 ${data.healthy ? 'text-green-600' : 'text-red-600'}`}>
                        {data.healthy ? (
                            <>
                                <CheckCircle size={18} />
                                ✅ سليمة
                            </>
                        ) : (
                            <>
                                <AlertTriangle size={18} />
                                ⚠️ تحذير
                            </>
                        )}
                    </span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                    <span className="text-gray-600 font-medium">الموظفون</span>
                    <span className="text-blue-700 font-bold">{data.activeAgents} نشط</span>
                </div>

                <div className="flex items-center justify-between py-2">
                    <span className="text-gray-600 font-medium">العمليات</span>
                    <span className="text-blue-700 font-bold">{data.activeOperations} جارية</span>
                </div>
            </div>

            <button
                className="mt-4 w-full text-blue-700 hover:bg-blue-50 py-2 rounded-md border border-blue-700 transition-colors font-semibold"
                onClick={handleClick}
            >
                التفاصيل →
            </button>
        </div>
    );
};
