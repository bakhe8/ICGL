
import React from 'react';
import { FileText, CheckCircle2, XCircle, Clock, Trash2 } from 'lucide-react';
import type { ADR } from '../../types';

interface ADRFeedProps {
    adrs: ADR[];
    onDelete?: (adrId: string) => void;
}

export const ADRFeed: React.FC<ADRFeedProps> = ({ adrs, onDelete }) => {
    const getStatusIcon = (status: string) => {
        if (status === 'ACCEPTED') return <CheckCircle2 size={16} className="text-emerald-400" />;
        if (status === 'REJECTED') return <XCircle size={16} className="text-red-400" />;
        return <Clock size={16} className="text-amber-400" />;
    };

    return (
        <div className="glass-panel h-full flex flex-col">
            <div className="p-4 border-b border-white/5 flex justify-between items-center glass-header rounded-t-xl">
                <h3 className="font-semibold text-white/90 flex items-center gap-2">
                    <FileText size={16} className="text-purple-400" />
                    Recent Decisions (ADRs)
                </h3>
                <span className="text-xs text-white/40">{adrs.length} Records</span>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-white/10">
                {adrs.length === 0 ? (
                    <div className="text-center text-white/30 py-10 text-sm">No decisions recorded yet.</div>
                ) : (
                    adrs.map((adr) => (
                        <div key={adr.id} className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group">
                            <div className="flex justify-between items-start mb-1">
                                <span className={`text-xs font-mono px-1.5 py-0.5 rounded border ${adr.status === 'ACCEPTED' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' :
                                    adr.status === 'REJECTED' ? 'bg-red-500/10 border-red-500/20 text-red-300' :
                                        'bg-amber-500/10 border-amber-500/20 text-amber-300'
                                    }`}>
                                    {getStatusIcon(adr.status)}
                                    <span className="ml-1">{adr.status}</span>
                                </span>
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] text-white/30 font-mono">
                                        {new Date(adr.created_at).toLocaleDateString()}
                                    </span>
                                    {onDelete && (
                                        <button
                                            onClick={() => onDelete(adr.id)}
                                            title="Delete ADR"
                                            className="opacity-0 group-hover:opacity-100 transition-opacity text-red-300 hover:text-red-200"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    )}
                                </div>
                            </div>
                            <div className="font-medium text-sm text-white/90 mb-1 group-hover:text-purple-300 transition-colors">
                                {adr.id}: {adr.title}
                            </div>
                            <div className="text-xs text-white/50 line-clamp-2">
                                {adr.context}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
