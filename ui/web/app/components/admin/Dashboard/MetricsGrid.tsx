import { MetricsGrid as MetricsGridView, type SystemStatusSummary } from '@icgl/ui-components';
import type { SystemStatus } from '../../../api/types';

interface MetricsGridProps {
    status: SystemStatus | null;
}

export const MetricsGrid = ({ status }: MetricsGridProps) => {
    const mapped: SystemStatusSummary | null = status
        ? {
            active_alert_level: status.active_alert_level,
            waiting_for_human: status.waiting_for_human,
            telemetry: {
                drift_detection_count: status.telemetry.drift_detection_count,
                last_latency_ms: status.telemetry.last_latency_ms,
            },
        }
        : null;

    return <MetricsGridView status={mapped} />;
};

export default MetricsGrid;
