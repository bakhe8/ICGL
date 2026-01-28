import { Link } from '@tanstack/react-router';
import {
    Activity,
    BarChart3,
    BrainCircuit,
    Code2,
    FileCode,
    History,
    Home,
    Layout,
    Library,
    Map,
    MessageSquare,
    MessageSquareText,
    Network,
    Radio,
    ShieldCheck,
    Sparkles
} from 'lucide-react';

const navItems = [
    { label: 'Cockpit', icon: Home, to: '/dashboard' },
    { label: 'المحادثة السيادية', icon: MessageSquare, to: '/chat' },
    { label: 'مساحة التفكير', icon: BrainCircuit, to: '/idea' },
    { label: 'إرث التفكير', icon: History, to: '/timeline' },
    { label: 'سجل الوكلاء', icon: Network, to: '/registry' },
    { label: 'مختبر الحوكمة', icon: ShieldCheck, to: '/governance-lab' },
    { label: 'خارطة الطريق', icon: Map, to: '/roadmap' },
    { label: 'الذاكرة الفكرية', icon: Library, to: '/mind' },
    { label: 'سلامة العقل', icon: ShieldCheck, to: '/security' },

    { type: 'header', label: 'الطبقة السيادية — Sovereignty' },
    { label: 'لوحة القيادة (Admin)', icon: Layout, to: '/admin/dashboard' },
    { label: 'تحكم النواة (NCCI)', icon: Sparkles, to: '/admin/ncci' },
    { label: 'تتبع العمليات', icon: Radio, to: '/admin/observability' },

    { type: 'header', label: 'مستوى التحكم (SCP)' },
    { label: 'نظرة عامة SCP', icon: BarChart3, to: '/admin/scp/overview' },
    { label: 'الأحداث الحية', icon: Activity, to: '/admin/scp/events' },
    { label: 'قنوات الاتصال', icon: Network, to: '/admin/scp/channels' },
    { label: 'تتبع SCP', icon: Code2, to: '/admin/scp/traces' },
    { label: 'السياسات', icon: ShieldCheck, to: '/admin/scp/policies' },
    { label: 'مركز التنسيق (COC)', icon: MessageSquareText, to: '/admin/scp/coc' },

    { label: 'وثائق API', icon: FileCode, href: '/docs' },
];

export default function SidebarNav() {
    return (
        <nav className="flex flex-col gap-2 p-4">
            {navItems.map((item, idx) => {
                if (item.type === 'header') {
                    return (
                        <div key={`header-${idx}`} className="mt-6 mb-2 px-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                            {item.label}
                        </div>
                    );
                }
                return item.to ? (
                    <Link
                        key={item.to}
                        to={item.to}
                        className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-600 hover:bg-brand-soft hover:text-brand-base transition-all group [&.active]:bg-brand-base [&.active]:text-white [&.active]:shadow-lg active:scale-95"
                        activeProps={{ className: 'active' }}
                        activeOptions={{ exact: true }}
                    >
                        {item.icon && <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform" />}
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
                        {item.icon && <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform" />}
                        <span className="font-semibold">{item.label}</span>
                    </a>
                )
            })}
        </nav>
    );
}
