import { Link } from '@tanstack/react-router';
import {
    BrainCircuit,
    Cog,
    FileCode,
    History,
    Home,
    Library,
    Map,
    MessageSquare,
    Network,
    ShieldCheck,
} from 'lucide-react';

// تنقل موحد يوضح كل الواجهات المعلنة (الحقيقية والحالية/الموك) بدون إخفاء أي صفحة.
const navItems = [
    { label: 'Cockpit', icon: Home, to: '/dashboard' },
    { label: 'المحادثة', icon: MessageSquare, to: '/chat' },
    { label: 'مساحة التفكير', icon: BrainCircuit, to: '/idea' },
    { label: 'إرث التفكير', icon: History, to: '/timeline' },
    { label: 'إدارة الوكلاء', icon: Network, to: '/agents-flow' },
    { label: 'القدرات', icon: Library, to: '/capabilities' },
    { label: 'خارطة الطريق', icon: Map, to: '/roadmap' },
    { label: 'الذاكرة الفكرية', icon: Library, to: '/mind' },
    { label: 'مخطط العقل الموسع', icon: BrainCircuit, to: '/mind/graph' },
    { label: 'سلامة العقل', icon: ShieldCheck, to: '/security' },
    { label: 'مركز العمليات', icon: Cog, to: '/operations' },
    { label: 'وثائق API', icon: FileCode, href: '/docs' },
    // رابط مباشر لصفحة الهبوط الثابتة لتجنب 404 على /ui/
    // بوابة الإدارة تُخدم الآن من admin/dist عبر /admin
    { label: 'بوابة الإدارة', icon: Cog, href: '/admin' },
];

export default function SidebarNav() {
    return (
        <nav className="flex flex-col gap-2 p-4">
            {navItems.map((item) => (
                item.to ? (
                    <Link
                        key={item.to}
                        to={item.to}
                        className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-600 hover:bg-brand-soft hover:text-brand-base transition-all group [&.active]:bg-brand-base [&.active]:text-white [&.active]:shadow-lg active:scale-95"
                        activeProps={{ className: 'active' }}
                        activeOptions={{ exact: true }} // يمنع تفعيل رابط الذاكرة الفكرية عند فتح مخطط العقل الموسع والعكس
                    >
                        <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        <span className="font-semibold">{item.label}</span>
                    </Link>
                ) : (
                    <a
                        key={item.href}
                        href={item.href}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-600 hover:bg-brand-soft hover:text-brand-base transition-all group active:scale-95"
                    >
                        <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        <span className="font-semibold">{item.label}</span>
                    </a>
                )
            ))}
        </nav>
    );
}
