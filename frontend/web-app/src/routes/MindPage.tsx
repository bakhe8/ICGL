
import { useMutation, useQuery } from '@tanstack/react-query';
import { ArrowLeftRight, BookOpen, FileSearch, FileText, Files, Network } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { fetchDocContent, fetchDocsTree, saveDocContent } from '../queries';
import useCockpitStore from '../state/cockpitStore';
import type { DocContentResponse, DocNode } from '../types';

// --- Graph Types & Interfaces ---
// (Moved to backend/types if shared, local here for force-graph)

// --- Sub-Component: Document Tree Item ---
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

// --- Main Page ---
export default function MindPage() {
    const [activeView, setActiveView] = useState<'memory' | 'graph'>('memory');

    // -- Memory State --
    const { setSelectedDoc } = useCockpitStore();
    const [selectedDocPath, setSelectedDocPath] = useState<string>();
    const [docDraft, setDocDraft] = useState<string>('');
    const [isEditingDoc, setIsEditingDoc] = useState(false);
    const [toast, setToast] = useState<string | null>(null);

    // -- Graph State --
    const fgRef = useRef<any>(null);
    const [dimensions, setDimensions] = useState({ w: 800, h: 600 });
    const graphContainerRef = useRef<HTMLDivElement>(null);

    // -- Queries --
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

    const { data: graphData } = useQuery({
        queryKey: ['mind-graph'],
        queryFn: async () => {
            // Re-using the logic from ExtendedMindPage
            // In a real implementation this endpoint matches /api/mind/graph
            const res = await fetch('/api/mind/graph');
            if (!res.ok) return { nodes: [], links: [] };
            return res.json();
        },
        enabled: activeView === 'graph',
        staleTime: 60_000,
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

    // -- Effects --
    useEffect(() => {
        if (docContentData?.content !== undefined) {
            // Only update if not currently editing (or initial load)

            setDocDraft(docContentData.content);
        }
    }, [docContentData?.content]);

    useEffect(() => {
        const resize = () => {
            if (graphContainerRef.current) {
                setDimensions({
                    w: graphContainerRef.current.clientWidth,
                    h: graphContainerRef.current.clientHeight || 500,
                });
            }
        };
        window.addEventListener('resize', resize);
        if (activeView === 'graph') setTimeout(resize, 100);
        return () => window.removeEventListener('resize', resize);
    }, [activeView]);


    const docs = docsData?.roots ?? [];
    const canEditDoc = !!selectedDocPath && (selectedDocPath.toLowerCase().includes('policy') || selectedDocPath.startsWith('kb/'));

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
            {toast && (
                <div className="fixed top-3 right-3 z-50 px-4 py-2 rounded-lg bg-emerald-600 text-white shadow-panel text-sm">
                    {toast}
                    <button className="ml-2 text-xs underline" onClick={() => setToast(null)}>إغلاق</button>
                </div>
            )}

            <header className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse"></span>
                        <p className="text-[10px] font-black text-violet-500 uppercase tracking-widest">Sovereign Cognition</p>
                    </div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight">The Mind</h1>
                    <p className="text-slate-500 mt-2">Explore the institutional memory (Docs) or the cognitive connections (Graph).</p>
                </div>

                <div className="flex bg-slate-100/80 p-1.5 rounded-xl border border-slate-200">
                    <button
                        onClick={() => setActiveView('memory')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeView === 'memory' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                            }`}
                    >
                        <Files className="w-4 h-4" />
                        Memory Tree
                    </button>
                    <button
                        onClick={() => setActiveView('graph')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeView === 'graph' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                            }`}
                    >
                        <Network className="w-4 h-4" />
                        Cognitive Graph
                    </button>
                </div>
            </header>

            {activeView === 'memory' ? (
                <div className="grid lg:grid-cols-12 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="lg:col-span-4 glass rounded-3xl p-6 space-y-4 max-h-[80vh] overflow-hidden flex flex-col">
                        <h3 className="font-semibold text-ink flex items-center gap-2">
                            <Files className="w-5 h-5 text-brand-base" />
                            File Explorer
                        </h3>
                        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            {docs.map((node) => (
                                <DocumentNodeItem
                                    key={node.path}
                                    node={node}
                                    onSelect={(path) => {
                                        setSelectedDocPath(path);
                                        setSelectedDoc(path);
                                    }}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="lg:col-span-8 glass rounded-3xl p-6 space-y-4 flex flex-col min-h-[500px]">
                        <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-ink flex items-center gap-2">
                                <FileSearch className="w-5 h-5 text-brand-base" />
                                {selectedDocPath ? selectedDocPath : 'Preview'}
                            </h3>
                            {selectedDocPath && (
                                <button
                                    className={`px-4 py-2 rounded-xl text-sm border transition ${canEditDoc
                                        ? 'bg-brand-base text-white hover:bg-brand-deep'
                                        : 'bg-slate-100 text-slate-400'
                                        }`}
                                    onClick={() => setIsEditingDoc((v) => !v)}
                                    disabled={!canEditDoc || saveDocMutation.isPending}
                                >
                                    {isEditingDoc ? 'Cancel' : 'Edit Document'}
                                </button>
                            )}
                        </div>

                        <div className="flex-1 bg-white rounded-2xl border border-slate-200 overflow-hidden relative">
                            {selectedDocPath ? (
                                docContentData ? (
                                    isEditingDoc ? (
                                        <div className="flex flex-col h-full">
                                            <textarea
                                                className="flex-1 p-4 w-full h-full resize-none focus:outline-none font-mono text-sm"
                                                value={docDraft}
                                                onChange={(e) => setDocDraft(e.target.value)}
                                            />
                                            <div className="p-2 bg-slate-50 border-t border-slate-200 flex justify-end gap-2">
                                                <button
                                                    onClick={() => saveDocMutation.mutate({ path: selectedDocPath!, content: docDraft })}
                                                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-bold"
                                                >
                                                    Save Changes
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="p-6 overflow-auto h-full">
                                            <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                                                {docContentData.content}
                                            </pre>
                                        </div>
                                    )
                                ) : (
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <div className="w-8 h-8 border-4 border-brand-base border-t-transparent rounded-full animate-spin"></div>
                                    </div>
                                )
                            ) : (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
                                    <BookOpen className="w-12 h-12 mb-3 opacity-20" />
                                    <p>Select a document to view</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="glass rounded-3xl p-0 overflow-hidden h-[700px] relative animate-in fade-in slide-in-from-bottom-4 duration-500" ref={graphContainerRef}>
                    {graphData ? (
                        <ForceGraph2D
                            ref={fgRef}
                            width={dimensions.w}
                            height={dimensions.h}
                            graphData={graphData}
                            nodeLabel="label"
                            nodeColor={(node: any) => node.color || '#6366f1'}
                            nodeRelSize={6}
                            linkColor={() => 'rgba(150,150,150,0.2)'}
                            linkWidth={1.5}
                            linkDirectionalParticles={2}
                            linkDirectionalParticleSpeed={0.005}
                            backgroundColor="rgba(255,255,255,0)"
                        />
                    ) : (
                        <div className="flex items-center justify-center h-full">Loading Neural Network...</div>
                    )}
                    <div className="absolute bottom-4 left-4 bg-white/80 p-3 rounded-xl backdrop-blur-sm text-xs border border-slate-200 shadow-sm">
                        <p className="font-bold mb-1">Graph Legend</p>
                        <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-indigo-500"></span> Concept</div>
                        <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Strategy</div>
                    </div>
                </div>
            )}
        </div>
    );
}
