
import React from 'react';
import {
    MessageSquare,
    LayoutDashboard,
    Settings,
    ShieldAlert,
    Cpu,
    Activity
} from 'lucide-react';

interface LayoutProps {
    children: React.ReactNode;
    activeTab: 'chat' | 'dashboard' | 'scp' | 'observability';
    onTabChange: (tab: 'chat' | 'dashboard' | 'scp' | 'observability') => void;
}

const Layout: React.FC<LayoutProps> = ({ children, activeTab, onTabChange }) => {
    return (
        <div className="flex h-screen w-full bg-[#0d0d12] text-white overflow-hidden font-sans">
            {/* Sidebar */}
            <aside className="w-64 glass-panel m-4 mr-0 flex flex-col justify-between p-4 bg-opacity-60 border-opacity-40 border-white/30">
                {/* Brand */}
                <div>
                    <div className="flex items-center gap-3 mb-8 px-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
                            <Cpu size={20} className="text-white" />
                        </div>
                        <h1 className="text-xl font-bold tracking-tight text-white/90">
                            ICGL <span className="text-purple-400 text-xs align-top">SYS</span>
                        </h1>
                    </div>

                    {/* Nav */}
                    <nav className="space-y-2">
                        <NavItem
                            icon={<MessageSquare size={18} />}
                            label="Conversation"
                            active={activeTab === 'chat'}
                            onClick={() => onTabChange('chat')}
                        />
                        <NavItem
                            icon={<LayoutDashboard size={18} />}
                            label="Dashboard"
                            active={activeTab === 'dashboard'}
                            onClick={() => onTabChange('dashboard')}
                        />
                        <NavItem
                            icon={<ShieldAlert size={18} />}
                            label="SCP"
                            active={activeTab === 'scp'}
                            onClick={() => onTabChange('scp')}
                        />
                        <NavItem
                            icon={<Activity size={18} />}
                            label="Observability"
                            active={activeTab === 'observability'}
                            onClick={() => onTabChange('observability')}
                        />
                    </nav>
                </div>

                {/* Footer */}
                <div className="space-y-2 pt-4 border-t border-white/5">
                    <div className="px-3 py-2 rounded-md hover:bg-white/5 cursor-pointer transition-colors flex items-center gap-3 text-white/50 hover:text-white/80">
                        <ShieldAlert size={18} />
                        <span className="text-sm font-medium">Sentinel Active</span>
                    </div>
                    <div className="px-3 py-2 rounded-md hover:bg-white/5 cursor-pointer transition-colors flex items-center gap-3 text-white/50 hover:text-white/80">
                        <Settings size={18} />
                        <span className="text-sm font-medium">Settings</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-full overflow-hidden relative">
                {/* Top Bar / Status */}
                <header className="h-16 flex items-center justify-between px-8 border-b border-white/5">
                    <div className="text-sm text-white/40">
                        System Status: <span className="text-emerald-400">Operational</span>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* User Profile placeholder */}
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/20"></div>
                    </div>
                </header>

                {/* Viewport */}
                <div className="flex-1 overflow-auto p-6 relative">
                    <div className="max-w-7xl mx-auto h-full flex flex-col">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
};

interface NavItemProps {
    icon: React.ReactNode;
    label: string;
    active: boolean;
    onClick: () => void;
}

const NavItem: React.FC<NavItemProps> = ({ icon, label, active, onClick }) => (
    <button
        onClick={onClick}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${active
            ? 'bg-purple-500/10 text-purple-300 border border-purple-500/20 shadow-lg shadow-purple-500/5'
            : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
    >
        <div className={`transition-colors ${active ? 'text-purple-400' : 'text-current'}`}>
            {icon}
        </div>
        <span className="text-sm font-medium">{label}</span>
        {active && (
            <div className="ml-auto w-1.5 h-1.5 rounded-full bg-purple-400 shadow-[0_0_8px_rgba(192,132,252,0.8)]" />
        )}
    </button>
);

export default Layout;
