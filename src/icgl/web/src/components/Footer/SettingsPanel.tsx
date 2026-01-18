import { useState } from 'react';
import { Settings, Moon, Sun, Monitor, Bell, Shield, Database, ChevronRight, Save } from 'lucide-react';

export const SettingsPanel = () => {
    const [activeSection, setActiveSection] = useState('general');

    const sections = [
        { id: 'general', label: 'General', icon: Settings },
        { id: 'appearance', label: 'Appearance', icon: Monitor },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'security', label: 'Security', icon: Shield },
        { id: 'system', label: 'System', icon: Database },
    ];

    return (
        <div className="h-full flex bg-white overflow-hidden animate-in slide-in-from-right-4 duration-500">
            {/* Sidebar */}
            <div className="w-1/4 min-w-[200px] border-l border-gray-200 bg-gray-50 flex flex-col p-2 gap-1">
                <div className="p-4 mb-2">
                    <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                        <Settings size={20} className="text-gray-400" />
                        Settings
                    </h2>
                </div>
                {sections.map(s => (
                    <button
                        key={s.id}
                        onClick={() => setActiveSection(s.id)}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${activeSection === s.id
                            ? 'bg-white text-blue-600 shadow-sm'
                            : 'text-gray-600 hover:bg-gray-100'
                            }`}
                    >
                        <s.icon size={18} />
                        {s.label}
                        {activeSection === s.id && <ChevronRight size={14} className="mr-auto ml-2" />}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="flex-1 p-8 overflow-y-auto">
                <div className="max-w-2xl mx-auto">
                    {/* Dynamic Content based on section */}
                    <div className="mb-8">
                        <h1 className="text-2xl font-bold text-gray-900 mb-2 capitalize">{activeSection} Settings</h1>
                        <p className="text-gray-500 text-sm">Manage your {activeSection} preferences for the Executive Platform.</p>
                    </div>

                    <div className="space-y-6">
                        {/* Example Settings Controls */}
                        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                            <h3 className="font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">Preferences</h3>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="font-medium text-gray-700">Language (اللغة)</div>
                                        <div className="text-xs text-gray-400">System display language</div>
                                    </div>
                                    <div className="flex items-center gap-2 border rounded-lg p-1 bg-gray-50">
                                        <button className="px-3 py-1 bg-white rounded shadow-sm text-sm font-medium text-blue-600">العربية</button>
                                        <button className="px-3 py-1 text-sm font-medium text-gray-500 hover:bg-gray-100 rounded">English</button>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="font-medium text-gray-700">Theme</div>
                                        <div className="text-xs text-gray-400">Interface appearance mode</div>
                                    </div>
                                    <div className="flex gap-2">
                                        <button className="p-2 rounded-lg bg-gray-100 text-gray-400 hover:bg-gray-200" title="Dark Mode (Disabled)">
                                            <Moon size={18} />
                                        </button>
                                        <button className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 shadow-sm" title="Light Mode (Executive)">
                                            <Sun size={18} />
                                        </button>
                                        <button className="p-2 rounded-lg bg-gray-100 text-gray-500 hover:bg-gray-200" title="System">
                                            <Monitor size={18} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                            <h3 className="font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">Identity</h3>
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-bold text-xl">
                                    CEO
                                </div>
                                <div>
                                    <div className="font-bold text-gray-900">Bakheet</div>
                                    <div className="text-xs text-gray-500">Chief Executive Officer • Level 0 Access</div>
                                </div>
                                <button className="mr-auto px-4 py-2 border border-blue-200 text-blue-600 rounded-lg text-sm font-medium hover:bg-blue-50">
                                    Manage Profile
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 flex justify-end">
                        <button className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg font-bold shadow-lg hover:bg-blue-700 transition-all hover:-translate-y-0.5">
                            <Save size={18} />
                            Save Changes
                        </button>
                    </div>

                </div>
            </div>
        </div>
    );
};
