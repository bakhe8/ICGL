import { Bot, Zap } from 'lucide-react';

interface ConsultationLink {
    from: string;
    to: string;
    type: string;
}

export function CouncilPulse({ consultations }: { consultations: ConsultationLink[] }) {
    return (
        <div className="relative h-24 w-full flex items-center justify-center overflow-hidden rounded-2xl glass-panel mt-4 px-6">
            <div className="absolute inset-0 bg-gradient-to-r from-brand-primary/5 via-transparent to-brand-primary/5 animate-pulse" />

            <div className="flex items-center gap-8 relative z-10 w-full justify-between">
                <div className="flex flex-col items-center gap-1 group">
                    <div className="p-2 rounded-lg bg-brand-soft/50 text-brand-base sovereign-glow">
                        <Bot className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold text-slate-600">ARCHITECT</span>
                </div>

                <div className="flex-1 flex items-center justify-center relative">
                    <div className="w-full h-[1px] bg-gradient-to-r from-transparent via-brand-primary/30 to-transparent" />
                    <Zap className="w-3 h-3 text-brand-accent absolute animate-bounce" />
                    <span className="absolute -top-4 text-[9px] uppercase tracking-widest text-brand-base font-black">
                        Consensus Pulse
                    </span>
                </div>

                <div className="flex flex-col items-center gap-1 group">
                    <div className="p-2 rounded-lg bg-emerald-100/50 text-emerald-700 border border-emerald-200">
                        <Bot className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold text-slate-600">COUNCIL PEERS</span>
                </div>
            </div>

            {/* Dynamic Links simulation */}
            {consultations.map((_, i) => (
                <div
                    key={i}
                    className="absolute council-link w-1/2 left-1/4 animate-float"
                    style={{
                        top: `${30 + (i * 10)}%`,
                        opacity: 0.1 + ((i * 7) % 30) / 100
                    }}
                />
            ))}
        </div>
    );
}
