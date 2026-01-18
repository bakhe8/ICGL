import { Bell, AlertTriangle, CheckCircle, Info, Clock } from 'lucide-react';

interface Notification {
    id: string;
    type: 'alert' | 'success' | 'info';
    title: string;
    message: string;
    time: string;
    read: boolean;
}

export const NotificationsPanel = () => {
    const notifications: Notification[] = [
        {
            id: '1',
            type: 'alert',
            title: 'تنبيه أمني: محاولة وصول غير مصرح',
            message: 'رصد نظام Sentinel محاولة وصول غريبة من IP خارجي وتم حظرها.',
            time: 'منذ 10 دقائق',
            read: false
        },
        {
            id: '2',
            type: 'info',
            title: 'تقرير الأداء الأسبوعي جاهز',
            message: 'يمكنك الآن الاطلاع على ملخص أداء الوكلاء الذكيين لهذا الأسبوع.',
            time: 'منذ ساعة',
            read: false
        },
        {
            id: '3',
            type: 'success',
            title: 'تم اكتمال تحديث السياسات',
            message: 'تم نشر السياسات الجديدة بنجاح وتعميمها على الأقسام.',
            time: 'منذ ساعتين',
            read: true
        },
        {
            id: '4',
            type: 'info',
            title: 'تذكير: اجتماع المراجعة الاستراتيجية',
            message: 'لديك اجتماع مجدول غداً الساعة 10:00 صباحاً.',
            time: 'أمس',
            read: true
        }
    ];

    const getIcon = (type: Notification['type']) => {
        switch (type) {
            case 'alert': return <AlertTriangle className="text-red-500" size={20} />;
            case 'success': return <CheckCircle className="text-green-500" size={20} />;
            case 'info': return <Info className="text-blue-500" size={20} />;
        }
    };

    return (
        <div className="h-full flex flex-col bg-[#F8FAFC]">
            {/* Context Header */}
            <div className="p-8 pb-4 bg-white border-b border-gray-100">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-blue-50 rounded-lg">
                        <Bell className="text-blue-600" size={24} />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">مركز الإشعارات</h2>
                        <p className="text-gray-500 text-sm">آخر التحديثات والتنبيهات في النظام</p>
                    </div>
                </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
                {notifications.map((note) => (
                    <div
                        key={note.id}
                        className={`p-5 rounded-2xl border transition-all hover:bg-white hover:shadow-sm flex gap-4 ${note.read ? 'bg-gray-50/50 border-transparent opacity-70' : 'bg-white border-blue-100 shadow-sm'
                            }`}
                    >
                        <div className={`mt-1 p-2 rounded-full ${note.type === 'alert' ? 'bg-red-50' :
                                note.type === 'success' ? 'bg-green-50' : 'bg-blue-50'
                            }`}>
                            {getIcon(note.type)}
                        </div>
                        <div className="flex-1">
                            <div className="flex justify-between items-start mb-1">
                                <h3 className={`font-bold text-base ${note.read ? 'text-gray-700' : 'text-gray-900'}`}>
                                    {note.title}
                                </h3>
                                {!note.read && (
                                    <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                                )}
                            </div>
                            <p className="text-gray-600 text-sm leading-relaxed mb-3">
                                {note.message}
                            </p>
                            <div className="flex items-center gap-2 text-xs text-gray-400 font-medium tracking-wide">
                                <Clock size={12} />
                                <span>{note.time}</span>
                            </div>
                        </div>
                    </div>
                ))}

                {notifications.length === 0 && (
                    <div className="text-center py-20 text-gray-400">
                        <Bell size={48} className="mx-auto mb-4 opacity-20" />
                        <p>لا توجد إشعارات جديدة</p>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-gray-100 bg-white text-center">
                <button className="text-sm font-bold text-blue-600 hover:text-blue-700 hover:underline">
                    تحديد الكل كمقروء
                </button>
            </div>
        </div>
    );
};
