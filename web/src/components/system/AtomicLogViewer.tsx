import { useQuery } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { Archive, CheckCircle, RefreshCcw } from 'lucide-react';

type Transaction = {
    id: string;
    files: string[];
    status: 'staged' | 'committed' | 'rollback';
    timestamp: number; // backend returns timestamp in ms or seconds? backend uses ms.
    hash: string;
};

export default function AtomicLogViewer() {
    // Real Data Integration
    const { data: transactions = [] } = useQuery<Transaction[]>({
        queryKey: ['atomic-transactions'],
        queryFn: async () => {
            const res = await fetch('/api/ops/transactions');
            if (!res.ok) return [];
            const data = await res.json();
            return data;
        },
        refetchInterval: 3000, // Poll every 3s
    });

    return (
        <div className="glass rounded-3xl p-6 relative min-h-[300px] flex flex-col">
            <header className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <Archive className="w-5 h-5 text-emerald-600" />
                        Atomic Deployment Log
                    </h2>
                    <p className="text-xs text-slate-500">Transaction Manager History (backend/ops/transaction.py)</p>
                </div>
                <div className="bg-slate-100 p-2 rounded-lg text-xs font-mono text-slate-500">
                    Lock Status: <span className="text-emerald-600 font-bold">RELEASED</span>
                </div>
            </header>

            <div className="space-y-4 relative pl-4 border-l-2 border-slate-100 ml-2">
                <AnimatePresence>
                    {transactions.map((tx) => (
                        <motion.div
                            key={tx.id}
                            initial={{ opacity: 0, x: -20, height: 0 }}
                            animate={{ opacity: 1, x: 0, height: 'auto' }}
                            exit={{ opacity: 0 }}
                            className="relative pl-6 pb-2"
                        >
                            {/* Dot */}
                            <div className={`absolute -left-[21px] top-1 w-3 h-3 rounded-full border-2 border-white shadow-sm z-10 ${tx.status === 'committed' ? 'bg-emerald-500' :
                                    tx.status === 'rollback' ? 'bg-rose-500' : 'bg-slate-300'
                                }`} />

                            <div className="p-3 bg-white/50 border border-slate-200 rounded-xl shadow-sm">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className="font-mono text-xs font-bold text-slate-700">TX-{tx.id}</span>
                                        <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase font-bold ${tx.status === 'committed' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                                            }`}>
                                            {tx.status}
                                        </span>
                                    </div>
                                    <span className="text-[10px] text-slate-400 font-mono">{tx.hash}</span>
                                </div>

                                <div className="space-y-1">
                                    {tx.files.map(f => (
                                        <div key={f} className="text-xs text-slate-600 flex items-center gap-2">
                                            {tx.status === 'committed' ? <CheckCircle className="w-3 h-3 text-emerald-400" /> : <RefreshCcw className="w-3 h-3 text-rose-400" />}
                                            {f}
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-2 text-[10px] text-slate-400 flex justify-end">
                                    {new Date(tx.timestamp).toLocaleTimeString()}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                    {!transactions.length && (
                        <div className="text-sm text-slate-400 italic pt-10">Waiting for next transaction...</div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
