import { useCallback, useEffect, useState } from 'react';
import { TraceVisualization as TraceVisualizationView, type TraceGraph } from '@icgl/ui-components';

interface Props {
    traceId: string;
}

export function TraceVisualization({ traceId }: Props) {
    const [graph, setGraph] = useState<TraceGraph | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadTrace = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const baseUrl = 'http://127.0.0.1:8000';
            const res = await fetch(`${baseUrl}/observability/trace/${traceId}/graph`);

            if (!res.ok) {
                throw new Error(`Failed to load trace: ${res.statusText}`);
            }

            const data = await res.json();
            setGraph(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load trace');
        } finally {
            setLoading(false);
        }
    }, [traceId]);

    useEffect(() => {
        loadTrace();
    }, [loadTrace]);

    return (
        <TraceVisualizationView
            trace={graph}
            loading={loading}
            error={error}
            onRetry={loadTrace}
        />
    );
}

export default TraceVisualization;
