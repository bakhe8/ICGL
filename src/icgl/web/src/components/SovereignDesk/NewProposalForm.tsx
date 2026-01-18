import React, { useState } from 'react';

interface NewProposalFormProps {
    onSubmitted?: () => void;
}

export const NewProposalForm: React.FC<NewProposalFormProps> = ({ onSubmitted }) => {
    const [title, setTitle] = useState('');
    const [context, setContext] = useState('');
    const [decision, setDecision] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);
        try {
            const res = await fetch('/propose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, context, decision })
            });
            if (!res.ok) throw new Error('فشل إرسال الاقتراح');
            setSuccess(true);
            setTitle('');
            setContext('');
            setDecision('');
            if (onSubmitted) onSubmitted();
        } catch (e: any) {
            setError(e.message || 'خطأ غير معروف');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form className="bg-white rounded-2xl p-8 mb-8 shadow border border-gray-100" onSubmit={handleSubmit}>
            <h2 className="text-lg font-bold mb-4 text-gray-800">🖋️ إضافة اقتراح جديد</h2>
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-600 mb-1">العنوان</label>
                <input type="text" value={title} onChange={e => setTitle(e.target.value)} required className="w-full px-3 py-2 border rounded focus:outline-none focus:ring bg-gray-50 text-gray-900 placeholder-gray-400" placeholder="مثال: ترقية النظام" />
            </div>
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-600 mb-1">السياق</label>
                <textarea value={context} onChange={e => setContext(e.target.value)} required className="w-full px-3 py-2 border rounded focus:outline-none focus:ring bg-gray-50 text-gray-900 placeholder-gray-400" placeholder="لماذا هذا الاقتراح؟" />
            </div>
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-600 mb-1">القرار المقترح</label>
                <textarea value={decision} onChange={e => setDecision(e.target.value)} required className="w-full px-3 py-2 border rounded focus:outline-none focus:ring bg-gray-50 text-gray-900 placeholder-gray-400" placeholder="ما هو الإجراء المطلوب؟" />
            </div>
            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition" disabled={loading}>
                {loading ? 'جاري الإرسال...' : 'إرسال الاقتراح'}
            </button>
            {error && <div className="mt-3 text-red-500 text-sm">{error}</div>}
            {success && <div className="mt-3 text-green-500 text-sm">تم إرسال الاقتراح بنجاح!</div>}
        </form>
    );
};
