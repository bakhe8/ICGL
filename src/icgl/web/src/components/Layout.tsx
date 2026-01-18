import { useState } from 'react';
import {
    LayoutDashboard,
    MessageSquare,
    Archive,
    Menu,
    LogOut,
    Bell,
    Shield,
    Settings,
    X
} from 'lucide-react';
import { SovereignDesk } from './SovereignDesk/SovereignDesk';
import { SentinelPanel } from './Footer/SentinelPanel';
import { SettingsPanel } from './Footer/SettingsPanel';
import { NotificationsPanel } from './NotificationsPanel';
import { ChatContainer } from './Chat/ChatContainer';
import { SovereignArchive } from './SovereignArchive';

interface NavItemProps {
    item: { id: string; icon: React.ElementType; label: string; sub: string };
    isActive: boolean;
    isCollapsed: boolean;
    onClick: () => void;
}

const NavItem = ({ item, isActive, isCollapsed, onClick }: NavItemProps) => (
    <button
        onClick={onClick}
        className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 group relative overflow-hidden focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400/50 ${isActive
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
            : 'hover:bg-gray-100 text-gray-500 hover:text-gray-900'
            }`}
        title={item.label}
        aria-label={item.label}
        aria-current={isActive ? 'page' : undefined}
    >
        <div className={`relative z-10 flex items-center justify-center transition-transform duration-200 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`}>
            <item.icon size={22} className={isActive ? 'text-white' : 'text-current'} />
        </div>

        {!isCollapsed && (
            <div className="flex flex-col items-start relative z-10">
                <span className={`font-bold text-sm tracking-wide ${isActive ? 'text-white' : 'text-gray-800'}`}>
                    {item.label}
                </span>
                <span className={`text-[10px] uppercase font-bold tracking-wider ${isActive ? 'text-blue-200' : 'text-gray-400'}`}>
                    {item.sub}
                </span>
            </div>
        )}

        {isActive && (
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-700 to-blue-500 opacity-100 -z-0"></div>
        )}
    </button>
);

export const Layout = () => {
    const [activeTab, setActiveTab] = useState('sovereign');
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const [activeModal, setActiveModal] = useState<'none' | 'sentinel' | 'settings' | 'notifications'>('none');

    // Navigation Configuration - Simplified for Executive Focus
    const navItems = [
        { id: 'sovereign', icon: LayoutDashboard, label: 'المكتب الرئيسي', sub: 'Main Desk' },
        { id: 'chat', icon: MessageSquare, label: 'المستشار الذكي', sub: 'Assistant' },
        { id: 'archive', icon: Archive, label: 'الأرشيف والقرارات', sub: 'Archive' },
    ];

    const renderContent = () => {
        switch (activeTab) {
            case 'sovereign': return <SovereignDesk onTabChange={setActiveTab} />;
            case 'chat': return <ChatContainer />;
            case 'archive': return <SovereignArchive onTabChange={setActiveTab} />;
            default: return <SovereignDesk onTabChange={setActiveTab} />;
        }
    };



    return (
        <>
            {/* Accessibility Skip Link */}
            <a
                href="#main-content"
                className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:right-4 focus:z-[100] px-4 py-2 bg-blue-600 text-white font-bold rounded-lg shadow-xl"
            >
                تجاوز إلى المحتوى الرئيسي
            </a>

            {/* Sidebar */}
            <aside
                className={`${isSidebarCollapsed ? 'w-20' : 'w-72'} 
                bg-white border-l border-gray-200 shadow-xl z-50 flex flex-col transition-all duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] relative`}
                aria-label="القائمة الجانبية"
            >
                {/* Brand */}
                <div className="h-20 flex items-center justify-between px-6 border-b border-gray-100">
                    {!isSidebarCollapsed && (
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-200">
                                <span className="font-bold text-white text-lg" aria-hidden="true">S</span>
                            </div>
                            <div>
                                <h1 className="font-extrabold text-xl text-gray-900 tracking-tight">ICGL</h1>
                                <p className="text-[10px] text-gray-400 uppercase font-bold tracking-[0.2em]">Executive Layer</p>
                            </div>
                        </div>
                    )}
                    <button
                        onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                        className="p-2 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                        aria-label={isSidebarCollapsed ? "توسيع القائمة" : "طي القائمة"}
                        {...{ "aria-expanded": isSidebarCollapsed ? "false" : "true" }}
                    >
                        <Menu size={20} />
                    </button>
                </div>

                {/* Navigation Items */}
                <nav className="flex-1 py-8 px-4 space-y-2 overflow-y-auto no-scrollbar" aria-label="التنقل الرئيسي">
                    {navItems.map(item => (
                        <NavItem
                            key={item.id}
                            item={item}
                            isActive={activeTab === item.id}
                            isCollapsed={isSidebarCollapsed}
                            onClick={() => setActiveTab(item.id)}
                        />
                    ))}
                </nav>

                {/* Bottom Actions */}
                <div className="p-4 border-t border-gray-100 space-y-2 bg-gray-50/50">
                    <button
                        onClick={() => setActiveModal('sentinel')}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl hover:bg-blue-50 text-gray-500 hover:text-blue-600 transition-all group focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 ${isSidebarCollapsed ? 'justify-center' : ''}`}
                        title="حالة النظام"
                        aria-label="حالة النظام"
                    >
                        <Shield className="text-emerald-500" size={20} />
                        {!isSidebarCollapsed && <span className="font-bold text-sm text-gray-700">System Secure</span>}
                    </button>

                    <button
                        onClick={() => setActiveModal('settings')}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl hover:bg-blue-50 text-gray-500 hover:text-blue-600 transition-all group focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 ${isSidebarCollapsed ? 'justify-center' : ''}`}
                        title="الإعدادات"
                        aria-label="الإعدادات"
                    >
                        <Settings size={20} className="group-hover:rotate-90 transition-transform duration-500" />
                        {!isSidebarCollapsed && <span className="font-bold text-sm">Settings</span>}
                    </button>

                    <button
                        className={`w-full flex items-center gap-3 p-3 rounded-xl hover:bg-red-50 text-gray-500 hover:text-red-600 transition-all group focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500/50 ${isSidebarCollapsed ? 'justify-center' : ''}`}
                        title="تسجيل الخروج"
                        aria-label="تسجيل الخروج"
                    >
                        <LogOut size={20} className="group-hover:scale-110 transition-transform" />
                        {!isSidebarCollapsed && <span className="font-bold text-sm">تسجيل الخروج</span>}
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main id="main-content" className="flex-1 flex flex-col min-w-0 bg-[#F8FAFC]" tabIndex={-1}>
                {/* Top Bar */}
                <header className="h-16 bg-white border-b border-gray-200 px-8 flex items-center justify-between shadow-sm z-40">
                    <div className="flex items-center gap-4">
                        <h2 className="text-xl font-bold text-gray-800">
                            {navItems.find(i => i.id === activeTab)?.label || 'المكتب الرئيسي'}
                        </h2>
                        <span
                            className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-bold border border-blue-100 cursor-help"
                            title="النظام يعمل بكفاءة تامة ولا توجد مشاكل حرجة"
                            role="status"
                            aria-label="حالة النظام: نشط"
                        >
                            System Active
                        </span>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setActiveModal('notifications')}
                            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all relative focus:outline-none focus:ring-2 focus:ring-blue-500"
                            title="الإشعارات"
                            aria-label="الإشعارات: يوجد تنبيهات غير مقروءة"
                        >
                            <Bell size={20} />
                            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
                        </button>
                        <div className="h-8 w-px bg-gray-200"></div>
                        <div className="flex items-center gap-3 pl-2">
                            <div className="text-left hidden md:block">
                                <p className="text-sm font-bold text-gray-900">Bakheet</p>
                                <p className="text-xs text-gray-500 font-mono">CEO_OFFICE</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-gray-200 to-gray-300 border-2 border-white shadow-md" aria-hidden="true"></div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <div className="flex-1 overflow-y-auto no-scrollbar relative">
                    {renderContent()}
                </div>
            </main>

            {/* Modal Overlay */}
            {activeModal !== 'none' && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-white w-full max-w-4xl h-[80vh] rounded-3xl shadow-2xl overflow-hidden relative flex flex-col animate-in zoom-in-95 duration-300">
                        <button
                            onClick={() => setActiveModal('none')}
                            className="absolute top-4 left-4 z-50 p-2 bg-gray-100 hover:bg-red-50 text-gray-500 hover:text-red-500 rounded-full transition-colors"
                            aria-label="إغلاق النافذة"
                        >
                            <X size={20} />
                        </button>

                        <div className="flex-1 overflow-hidden relative" dir="ltr">
                            {activeModal === 'sentinel' && <SentinelPanel />}
                            {activeModal === 'settings' && <SettingsPanel />}
                            {activeModal === 'notifications' && <NotificationsPanel />}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};
