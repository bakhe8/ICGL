import { useQuery } from '@tanstack/react-query';
import { Maximize2, RefreshCw } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

interface GraphNode {
    id: string;
    label: string;
    type: string;
    color: string;
    val: number;
    x?: number;
    y?: number;
}

interface GraphLink {
    source: string;
    target: string;
    label?: string;
}

interface GraphData {
    nodes: GraphNode[];
    links: GraphLink[];
}

interface ForceGraphMethods {
    zoomToFit: (duration: number, padding?: number) => void;
    centerAt: (x: number, y: number, duration: number) => void;
    zoom: (k: number, duration: number) => void;
    emitParticle: (link: GraphLink) => void;
    d3Force: (forceName: string, forceFn?: unknown) => void;
    d3ReheatSimulation: () => void;
    pauseAnimation: () => void;
    resumeAnimation: () => void;
}

export default function ExtendedMindPage() {
    const fgRef = useRef<ForceGraphMethods | undefined>(undefined);
    const [dimensions, setDimensions] = useState({ w: 800, h: 600 });
    const containerRef = useRef<HTMLDivElement>(null);

    const { data: graphData, refetch, isLoading } = useQuery<GraphData>({
        queryKey: ['mind-graph'],
        queryFn: async () => {
            const res = await fetch('/api/mind/graph');
            if (!res.ok) throw new Error('Failed to fetch graph');
            return res.json();
        },
        initialData: { nodes: [], links: [] }
    });

    useEffect(() => {
        function resize() {
            if (containerRef.current) {
                setDimensions({
                    w: containerRef.current.clientWidth,
                    h: containerRef.current.clientHeight
                });
            }
        }
        window.addEventListener('resize', resize);
        resize();
        return () => window.removeEventListener('resize', resize);
    }, []);

    const zoomToFit = useCallback(() => {
        if (fgRef.current) {
            fgRef.current.zoomToFit(400);
        }
    }, [fgRef]);

    if (isLoading) return <div className="p-10 flex items-center justify-center">Loading Mind Graph...</div>;

    return (
        <div className="h-full flex flex-col space-y-4">
            <header className="glass rounded-3xl p-6 sm:p-8 shrink-0">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-extrabold text-ink leading-tight">
                            الذاكرة الممتدة <span className="text-brand-base">· Extended Mind</span>
                        </h1>
                        <p className="text-sm text-slate-600 mt-1">تصور مرئي للعلاقات بين المفاهيم، السياسات، والقرارات.</p>
                    </div>
                    <div className="flex gap-2">
                        <button onClick={() => refetch()} className="p-2 bg-slate-100 rounded-xl hover:bg-slate-200" title="Refresh">
                            <RefreshCw className="w-5 h-5 text-slate-600" />
                        </button>
                        <button onClick={zoomToFit} className="p-2 bg-slate-100 rounded-xl hover:bg-slate-200" title="Fit View">
                            <Maximize2 className="w-5 h-5 text-slate-600" />
                        </button>
                    </div>
                </div>
            </header>

            <div className="flex-1 glass rounded-3xl overflow-hidden relative" ref={containerRef}>
                <ForceGraph2D
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    ref={fgRef as any}
                    width={dimensions.w}
                    height={dimensions.h}
                    graphData={graphData}
                    nodeLabel="label"
                    nodeColor={(node: GraphNode) => node.color || '#999'}
                    nodeRelSize={6}
                    linkColor={() => 'rgba(150,150,150,0.2)'}
                    linkWidth={1.5}
                    linkDirectionalParticles={2}
                    linkDirectionalParticleSpeed={0.005}
                    backgroundColor="rgba(0,0,0,0)"
                    d3AlphaDecay={0.02}
                    d3VelocityDecay={0.3}
                    cooldownTicks={100}
                    onNodeClick={(node: GraphNode) => {
                        fgRef.current?.centerAt(node.x!, node.y!, 1000);
                        fgRef.current?.zoom(3, 1000);
                    }}
                />
            </div>
        </div>
    );
}
