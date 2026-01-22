import axios from 'axios';
import React, { useEffect, useState } from 'react';

interface Agent {
  id: number;
  name: string;
  status: string;
}

const OrgSidebar: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await axios.get<{ agents?: Agent[] }>('/api/system/agents');
        let agentsData: Agent[] = [];
        if (response.data && Array.isArray(response.data.agents)) {
          agentsData = response.data.agents;
        }
        setAgents(agentsData);
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Agents</h2>
      <ul>
        {agents.map(agent => (
          <li key={agent.id}>
            {agent.name} - {agent.status}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default OrgSidebar;