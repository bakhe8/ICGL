import { useQuery } from '@tanstack/react-query';
import { TechnicalCapabilities, type CapabilityGapGroup, type TechnicalAgent } from '@icgl/ui-components';
import React from 'react';
import { fetchAgentGaps, fetchAgentsRegistry } from '../api/queries';

const TechnicalCapabilitiesContainer: React.FC = () => {
  const agentsQuery = useQuery({
    queryKey: ['agents-registry'],
    queryFn: fetchAgentsRegistry,
    staleTime: 30_000,
  });

  const gapsQuery = useQuery({
    queryKey: ['agent-gaps'],
    queryFn: fetchAgentGaps,
    staleTime: 60_000,
  });

  const agents: TechnicalAgent[] =
    agentsQuery.data?.agents.map((agent) => ({
      id: agent.id,
      name: agent.name,
      role: agent.role,
      status: agent.status,
      description: agent.description,
    })) ?? [];

  const gaps: CapabilityGapGroup = {
    critical: gapsQuery.data?.critical ?? [],
    medium: gapsQuery.data?.medium ?? [],
    enhancement: gapsQuery.data?.enhancement ?? [],
  };

  return (
    <TechnicalCapabilities
      agents={agents}
      gaps={gaps}
      isAgentsLoading={agentsQuery.isLoading || agentsQuery.isFetching}
      isGapsLoading={gapsQuery.isLoading || gapsQuery.isFetching}
    />
  );
};

export default TechnicalCapabilitiesContainer;
