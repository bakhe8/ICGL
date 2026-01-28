
import type { ReactNode } from 'react';

interface GlassPanelProps {
    children: ReactNode;
    className?: string;
    variant?: 'glow' | 'flat' | 'heavy';
}

export function GlassPanel({ children, className = '', variant = 'flat' }: GlassPanelProps) {
    const baseClass = "rounded-3xl p-6 backdrop-blur-md transition-all";

    const variants = {
        glow: "bg-white/60 border border-white/50 shadow-xl sovereign-glow hover:shadow-2xl hover:bg-white/70",
        flat: "bg-white/40 border border-white/30 shadow-sm hover:bg-white/50",
        heavy: "bg-slate-900/90 text-white border border-slate-700 shadow-2xl"
    };

    return (
        <div className={`${baseClass} ${variants[variant]} ${className}`}>
            {children}
        </div>
    );
}
