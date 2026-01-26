import { CheckCircle2, Circle } from 'lucide-react';

interface PipelineStep {
    id: string;
    label: string;
    status: 'pending' | 'active' | 'completed' | 'skipped';
}

interface GovernancePipelineProps {
    currentStatus: string;
    adrId?: string | null;
}

export function GovernancePipeline({ currentStatus, adrId }: GovernancePipelineProps) {
    const steps: PipelineStep[] = [
        { id: '1', label: 'Idea Native Understanding', status: adrId ? 'completed' : 'active' },
        { id: '2', label: 'Policy Check (Gate)', status: currentStatus.includes('Policy') ? 'active' : (adrId ? 'completed' : 'pending') },
        { id: '3', label: 'Architect Summoning', status: currentStatus.includes('Architect') ? 'active' : (currentStatus.includes('Analysis') || currentStatus.includes('Council') ? 'completed' : 'pending') },
        { id: '4', label: 'Council Deliberation', status: currentStatus.includes('Council') || currentStatus.includes('Analysis') ? 'active' : (currentStatus.includes('Sovereign') ? 'completed' : 'pending') },
        { id: '5', label: 'Sovereign Decision', status: currentStatus.includes('Sovereign') || currentStatus.includes('Decision') ? 'active' : 'pending' },
    ];

    return (
        <div className="w-full flex items-center justify-between py-6 px-4 bg-white border-b border-slate-100">
            {steps.map((step, idx) => (
                <div key={step.id} className="flex items-center flex-1 last:flex-none">
                    <div className="flex flex-col items-center relative group">
                        <div className={`
                            w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-500
                            ${step.status === 'completed' ? 'bg-indigo-600 border-indigo-600 text-white' :
                                step.status === 'active' ? 'bg-white border-indigo-600 text-indigo-600 animate-pulse' :
                                    'bg-slate-50 border-slate-200 text-slate-300'}
                        `}>
                            {step.status === 'completed' ? <CheckCircle2 className="w-5 h-5" /> : <Circle className="w-5 h-5 fill-current" />}
                        </div>
                        <span className={`
                            absolute top-10 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap transition-colors
                            ${step.status === 'active' ? 'text-indigo-600' : 'text-slate-400'}
                        `}>
                            {step.label}
                        </span>
                    </div>
                    {idx < steps.length - 1 && (
                        <div className="flex-1 px-4">
                            <div className={`h-0.5 w-full rounded-full transition-all duration-700 ${step.status === 'completed' ? 'bg-indigo-600' : 'bg-slate-200'
                                }`} />
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
