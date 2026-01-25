import { useQuery } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
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

    const { data: graphData, isLoading } = useQuery<GraphData>({
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


    if (isLoading) return <div className="p-10 flex items-center justify-center">Loading Mind Graph...</div>;

    return (
        <div className="flex-1 flex flex-col space-y-4 pt-4">

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
