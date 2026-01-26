import { useRouter } from '@tanstack/react-router';
import { CouncilGrid as CouncilGridView, type CouncilAgent } from '@icgl/ui-components';
import type { AgentRegistryEntry } from '../../api/types';

interface CouncilGridProps {
    agents: AgentRegistryEntry[];
}

export function CouncilGrid({ agents }: CouncilGridProps) {
    const router = useRouter();

    const mappedAgents: CouncilAgent[] = agents.map((a) => ({
        id: a.id,
        name: a.name,
        status: a.status,
        department: a.department,
    }));

    return (
        <CouncilGridView
            agents={mappedAgents}
            onSelect={(id) => router.navigate({ to: '/agent/$agentId', params: { agentId: id } })}
        />
    );
}
