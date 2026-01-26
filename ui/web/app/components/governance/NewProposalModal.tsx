
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Send } from 'lucide-react';
import { createProposal } from '../../api/queries';

interface NewProposalModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const NewProposalModal: React.FC<NewProposalModalProps> = ({ isOpen, onClose }) => {
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState({
        title: '',
        context: '',
        decision: '',
        reason: '',
        impact: '',
    });

    const mutation = useMutation({
        mutationFn: () =>
            createProposal({
                title: formData.title,
                context: formData.context,
                decision: formData.decision || `Reason: ${formData.reason}\nImpact: ${formData.impact}`,
                reason: formData.reason,
                impact: formData.impact,
                human_id: 'operator',
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['proposals'] });
            queryClient.invalidateQueries({ queryKey: ['governanceDashboard'] });
            onClose();
            // Reset form
            setFormData({
                title: '',
                context: '',
                decision: '',
                reason: '',
                impact: '',
            });
        },
    });

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-800">
                    <div>
                        <h2 className="text-xl font-bold text-white">Create New Proposal (ADR)</h2>
                        <p className="text-sm text-slate-400">Propose an architectural or governance change.</p>
                    </div>
                    <button
                        onClick={onClose}
                        aria-label="Close proposal modal"
                        className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6 overflow-y-auto space-y-5 custom-scrollbar">

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Title</label>
                        <input
                            type="text"
                            placeholder="e.g. Implement Redis Caching for User Sessions"
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-base focus:border-transparent"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Context</label>
                        <textarea
                            placeholder="What is the current situation? Why do we need this change?"
                            className="w-full h-24 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-base focus:border-transparent resize-none"
                            value={formData.context}
                            onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Reason</label>
                            <textarea
                                placeholder="Why is this the best solution?"
                                className="w-full h-20 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-base focus:border-transparent resize-none"
                                value={formData.reason}
                                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Impact</label>
                            <textarea
                                placeholder="What will be affected? (Positive/Negative)"
                                className="w-full h-20 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-base focus:border-transparent resize-none"
                                value={formData.impact}
                                onChange={(e) => setFormData({ ...formData, impact: e.target.value })}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Decision Statement (optional)</label>
                        <textarea
                            placeholder="Summarize the decision in 1-2 lines."
                            className="w-full h-16 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-base focus:border-transparent resize-none"
                            value={formData.decision}
                            onChange={(e) => setFormData({ ...formData, decision: e.target.value })}
                        />
                    </div>

                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-800 flex justify-end gap-3 bg-slate-900/50">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 font-medium transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={() => mutation.mutate()}
                        disabled={mutation.isPending || !formData.title || !formData.context}
                        className="px-6 py-2 rounded-xl bg-brand-base text-white font-medium shadow-lg shadow-brand-base/20 hover:bg-brand-base/90 active:scale-95 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {mutation.isPending ? 'Submitting...' : 'Submit Proposal'}
                        {!mutation.isPending && <Send className="w-4 h-4 ml-1" />}
                    </button>
                </div>

            </div>
        </div>
    );
};
