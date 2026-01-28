import { useState } from 'react';
import { createProposal } from '../../../domains/desk/api';

import { GlassPanel } from '../../ui/GlassPanel';
import { SovereignButton } from '../../ui/SovereignButton';

interface NewProposalModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function NewProposalModal({ isOpen, onClose }: NewProposalModalProps) {
    const [title, setTitle] = useState('');
    const [context, setContext] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await createProposal({
                title,
                context,
                human_id: 'owner',
                decision: 'PROPOSED',
                reason: 'Initial proposal submission',
                impact: 'To be assessed'
            });
            onClose();
            setTitle('');
            setContext('');
        } catch (err) {
            console.error('Failed to create proposal', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm transition-opacity" onClick={onClose} />

            <div className="flex min-h-full items-center justify-center p-4">
                <div className="relative w-full max-w-md transform transition-all z-10">
                    <GlassPanel variant="heavy">
                        <div className="mb-4">
                            <h3 className="text-xl font-bold">
                                🌱 بذر فكرة جديدة (New Proposal)
                            </h3>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">
                                    عنوان الفكرة (Title)
                                </label>
                                <input
                                    type="text"
                                    required
                                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 focus:ring-2 focus:ring-brand-primary outline-none text-white"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="Ex: Optimize Agent Communication Protocol..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">
                                    السياق والمبررات (Context)
                                </label>
                                <textarea
                                    required
                                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 h-32 focus:ring-2 focus:ring-brand-primary outline-none text-white"
                                    value={context}
                                    onChange={(e) => setContext(e.target.value)}
                                    placeholder="Describe the context and desired outcome..."
                                />
                            </div>

                            <div className="flex justify-end gap-3 mt-6">
                                <SovereignButton variant="ghost" onClick={onClose} type="button">
                                    Cancel
                                </SovereignButton>
                                <SovereignButton type="submit" isLoading={isLoading}>
                                    Submit to Council
                                </SovereignButton>
                            </div>
                        </form>
                    </GlassPanel>
                </div>
            </div>
        </div>
    );
}
