import { useMutation, useQuery } from '@tanstack/react-query';
import { ArrowLeftRight, BookOpen, FileSearch, FileText } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchDocContent, fetchDocsTree, saveDocContent } from '../api/queries';
import type { DocContentResponse, DocNode } from '../api/types';
import useCockpitStore from '../state/cockpitStore';

function DocumentNodeItem({
    node,
    depth = 0,
    onSelect,
}: {
    node: DocNode;
    depth?: number;
    onSelect: (path: string) => void;
}) {
    const [open, setOpen] = useState(depth < 1);
    const hasChildren = node.children && node.children.length > 0;
    return (
        <div className="text-sm">
            <div
                className="flex items-center gap-2 py-1 cursor-pointer hover:text-brand-base"
                onClick={() => {
                    if (hasChildren) setOpen((v) => !v);
                    else onSelect(node.path);
                }}
            >
                {hasChildren ? (
                    <ArrowLeftRight className={`w-3.5 h-3.5 ${open ? 'text-brand-base' : 'text-slate-400'}`} />
                ) : (
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                )}
                <span>{node.name}</span>
            </div>
            {hasChildren && open && (
                <div className="pl-4 border-r border-dashed border-slate-200">
                    {node.children!.map((child) => (
                        <DocumentNodeItem key={child.path} node={child} depth={depth + 1} onSelect={onSelect} />
                    ))}
                </div>
            )}
        </div>
    );
}

export default function MindPage() {
    const { setSelectedDoc } = useCockpitStore();
    const [selectedDocPath, setSelectedDocPath] = useState<string>();
    const [docDraft, setDocDraft] = useState<string>('');
    const [isEditingDoc, setIsEditingDoc] = useState(false);
    const [toast, setToast] = useState<string | null>(null);

    const { data: docsData } = useQuery({
        queryKey: ['docs-tree'],
        queryFn: fetchDocsTree,
        retry: 1,
        staleTime: 120_000,
    });

    const { data: docContentData, refetch: refetchDocContent } = useQuery<DocContentResponse>({
        queryKey: ['doc-content', selectedDocPath],
        queryFn: () => fetchDocContent(selectedDocPath || ''),
        enabled: Boolean(selectedDocPath),
        retry: 1,
    });

    const saveDocMutation = useMutation({
        mutationFn: (payload: { path: string; content: string }) => saveDocContent(payload),
        onSuccess: () => {
            setToast('تم حفظ المستند بنجاح');
            setIsEditingDoc(false);
            refetchDocContent();
        },
        onError: (err: Error) => setToast(err.message || 'تعذر حفظ المستند'),
    });

    useEffect(() => {
        const content = docContentData?.content;
        if (content !== undefined) {
            setDocDraft(content);
            setIsEditingDoc(false);
        }
    }, [docContentData?.content]);

    const docs = docsData?.roots ?? [];
    const canEditDoc =
        !!selectedDocPath &&
        (selectedDocPath.toLowerCase().includes('policy') || selectedDocPath.startsWith('kb/'));

    return (
        <div className="space-y-6 pt-4">
            {toast && (
                <div className="fixed top-3 right-3 z-50 px-4 py-2 rounded-lg bg-emerald-600 text-white shadow-panel text-sm">
                    {toast}
                    <button className="ml-2 text-xs underline" onClick={() => setToast(null)}>
                        إغلاق
                    </button>
                </div>
            )}

            <section className="grid lg:grid-cols-2 gap-6">
                <div className="glass rounded-3xl p-6 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <Files className="w-5 h-5 text-brand-base" />
                            هيكل المستندات
                        </h3>
                    </div>
                    <div className="max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                        {docs.map((node) => (
                            <DocumentNodeItem
                                key={node.path}
                                node={node}
                                onSelect={(path) => {
                                    setSelectedDocPath(path);
                                    setSelectedDoc(path);
                                    setIsEditingDoc(false);
                                }}
                            />
                        ))}
                    </div>
                </div>

                <div className="glass rounded-3xl p-6 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <FileSearch className="w-5 h-5 text-brand-base" />
                            معاينة وتحرير
                        </h3>
                        {selectedDocPath && (
                            <button
                                className={`px-4 py-2 rounded-xl text-sm border transition ${canEditDoc
                                    ? 'bg-brand-base text-white border-brand-base shadow-sm hover:bg-brand-deep'
                                    : 'bg-slate-100 text-slate-400 border-slate-200'
                                    }`}
                                onClick={() => setIsEditingDoc((v) => !v)}
                                disabled={!canEditDoc || saveDocMutation.isPending}
                            >
                                {isEditingDoc ? 'إلغاء التعديل' : 'تعديل المستند'}
                            </button>
                        )}
                    </div>

                    <div className="min-h-[400px]">
                        {selectedDocPath ? (
                            docContentData ? (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2 text-xs font-mono text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-200">
                                        <span className="text-brand-base">Path:</span>
                                        {selectedDocPath}
                                    </div>
                                    {isEditingDoc && canEditDoc ? (
                                        <div className="space-y-3">
                                            <textarea
                                                className="w-full min-h-[400px] rounded-2xl border border-slate-200 px-4 py-3 text-sm font-mono bg-white focus:outline-none focus:ring-2 focus:ring-brand-base/20 transition-all"
                                                value={docDraft}
                                                onChange={(e) => setDocDraft(e.target.value)}
                                            />
                                            <div className="flex items-center justify-end gap-3">
                                                <button
                                                    className="px-5 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition"
                                                    onClick={() => {
                                                        setIsEditingDoc(false);
                                                        setDocDraft(docContentData.content);
                                                    }}
                                                >
                                                    تراجع
                                                </button>
                                                <button
                                                    className="px-6 py-2 rounded-xl bg-emerald-600 text-white shadow-sm hover:bg-emerald-700 transition disabled:opacity-50"
                                                    onClick={() => saveDocMutation.mutate({ path: selectedDocPath!, content: docDraft })}
                                                    disabled={saveDocMutation.isPending}
                                                >
                                                    {saveDocMutation.isPending ? 'جاري الحفظ...' : 'حفظ التعديلات'}
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="p-4 rounded-2xl bg-white border border-slate-200 overflow-x-auto">
                                            <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                                                {docContentData.content}
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-[400px] text-slate-400 gap-3">
                                    <div className="w-12 h-12 rounded-full border-4 border-brand-base border-t-transparent animate-spin" />
                                    <p>جاري تحميل المحتوى...</p>
                                </div>
                            )
                        ) : (
                            <div className="flex flex-col items-center justify-center h-[400px] text-slate-400 border-2 border-dashed border-slate-200 rounded-3xl">
                                <BookOpen className="w-12 h-12 mb-2 opacity-20" />
                                <p>اختر مستنداً من القائمة الجانبية للمعاينة</p>
                            </div>
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
}

// Re-using Lucide icons previously imported but defining Files locally if needed (it wasn't imported from lucide-react above)
import { Files } from 'lucide-react';

