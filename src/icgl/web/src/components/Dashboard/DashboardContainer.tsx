import { useState, useEffect } from 'react';
import { MetricsGrid } from './MetricsGrid';
import { ADRFeed } from './ADRFeed';
import { LayoutDashboard } from 'lucide-react';
import type { SystemStatus, ADR } from '../../types';

export const DashboardContainer = () => {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [adrs, setAdrs] = useState<ADR[]>([]);
    const [loading, setLoading] = useState(true);


    const fetchData = async () => {
        try {
            const [statusRes, adrRes] = await Promise.all([
                fetch('/status'),
                fetch('/adrs')
            ]);

            if (statusRes.ok) setStatus(await statusRes.json());
            if (adrRes.ok) setAdrs(await adrRes.json());

        } catch (error) {
            console.error('Dashboard data fetch failed', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleDeleteAdr = (id: string) => {
        setAdrs(prev => prev.filter(a => a.id !== id));
    };

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="animate-pulse flex flex-col items-center">
                    <div className="h-12 w-12 bg-gray-200 rounded-full mb-4"></div>
                    <div className="h-4 w-32 bg-gray-200 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="p-8 h-full overflow-y-auto">
            {/* Header Section */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                        <LayoutDashboard className="text-blue-600" />
                        المنصة الشاملة
                    </h1>
                    <p className="text-gray-500 mt-1">نظرة عامة على صحة النظام والعمليات</p>
                </div>
                <div className="flex gap-2">
                    <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-bold border border-green-100 flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        System Online
                    </span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="mb-8">
                <MetricsGrid status={status} />
            </div>

            {/* Main Content Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* ADR Feed */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <h3 className="font-bold text-gray-800 text-lg flex items-center gap-2">
                            <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
                            الذاكرة المؤسسية (ADRs)
                        </h3>
                        <button className="text-xs text-blue-600 hover:text-blue-700 hover:underline">عرض الكل</button>
                    </div>
                    <ADRFeed adrs={adrs} onDelete={handleDeleteAdr} />
                </div>

                {/* Quick Actions / Side Panel */}
                <div className="space-y-6">
                    {/* Quick Actions Card */}
                    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                        <h3 className="font-bold text-gray-800 text-sm mb-4">إجراءات سريعة</h3>
                        <div className="text-center text-gray-400 text-sm py-4">
                            الوصول السريع معطل مؤقتاً
                        </div>
                    </div>

                    {/* System Insight */}
                    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-5 text-white shadow-lg">
                        <h3 className="font-bold text-lg mb-2">رؤية النظام</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-sm border-b border-gray-700 pb-2">
                                <span className="text-gray-400">كفاءة الأداء</span>
                                <span className="font-mono text-emerald-400 font-bold">98.2%</span>
                            </div>
                            <div className="flex justify-between items-center text-sm border-b border-gray-700 pb-2">
                                <span className="text-gray-400">زمن الاستجابة</span>
                                <span className="font-mono text-blue-400 font-bold">45ms</span>
                            </div>
                            <div className="pt-2">
                                <div className="text-xs text-gray-500 mb-1">استهلاك الموارد</div>
                                <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-500 w-[65%]"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
