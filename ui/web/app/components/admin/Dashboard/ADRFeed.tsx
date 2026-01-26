import { ADRFeed as ADRFeedView, type ADRRecord } from '@icgl/ui-components';
import type { ADR } from '../../../api/types';

interface ADRFeedProps {
    adrs: ADR[];
    onDelete?: (adrId: string) => void;
}

export const ADRFeed = ({ adrs, onDelete }: ADRFeedProps) => {
    const mapped: ADRRecord[] = adrs.map((adr) => ({
        id: adr.id,
        title: adr.title,
        status: adr.status,
        context: adr.context,
        created_at: adr.created_at,
    }));

    return <ADRFeedView adrs={mapped} onDelete={onDelete} />;
};

export default ADRFeed;
