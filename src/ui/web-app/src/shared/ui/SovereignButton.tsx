
import { Loader2 } from 'lucide-react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface SovereignButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    icon?: ReactNode;
}

export function SovereignButton({
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    icon,
    className = '',
    disabled,
    ...props
}: SovereignButtonProps) {

    const baseStyles = "rounded-xl font-bold transition-all active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "bg-brand-primary text-slate-900 sovereign-glow hover:bg-brand-primary/90 shadow-lg shadow-brand-primary/20",
        secondary: "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200",
        danger: "bg-rose-500/10 text-rose-600 hover:bg-rose-500/20 border border-rose-500/20",
        ghost: "bg-transparent text-slate-500 hover:text-slate-900 hover:bg-slate-100/50"
    };

    const sizes = {
        sm: "px-3 py-1.5 text-xs",
        md: "px-5 py-2.5 text-sm",
        lg: "px-8 py-4 text-base"
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
            disabled={isLoading || disabled}
            {...props}
        >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : icon}
            {children}
        </button>
    );
}
