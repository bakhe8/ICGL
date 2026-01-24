import axios from 'axios';
import { motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';

// Define the type for system metrics
interface SystemMetrics {
  chaosLevel: number;
  efficiency: number;
  databaseIntegrity: number;
}

// Define the type for committee members
interface CommitteeMember {
  name: string;
  role: string;
}

const SystemSoulPage: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [committeeMembers, setCommitteeMembers] = useState<CommitteeMember[]>([]);

  // Fetch system metrics and committee members data
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const metricsResponse = await axios.get<SystemMetrics>('/api/system/metrics');
        setMetrics(metricsResponse.data);
      } catch (error) {
        console.error('Error fetching system metrics:', error);
      }
    };

    const fetchCommitteeMembers = async () => {
      try {
        const membersResponse = await axios.get<CommitteeMember[]>('/api/system/committee');
        setCommitteeMembers(membersResponse.data);
      } catch (error) {
        console.error('Error fetching committee members:', error);
      }
    };

    fetchMetrics();
    fetchCommitteeMembers();

    // Set up a polling mechanism to update metrics every 30 seconds
    const intervalId = setInterval(fetchMetrics, 30000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-900 via-purple-900 to-indigo-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">System Soul</h1>

        {metrics && (
          <motion.div
            className="bg-white bg-opacity-10 p-6 rounded-lg shadow-lg mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <h2 className="text-2xl font-semibold mb-4">Current System Metrics</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span>Chaos Level:</span>
                <span>{metrics.chaosLevel}</span>
              </div>
              <div className="flex justify-between">
                <span>Efficiency:</span>
                <span>{metrics.efficiency}</span>
              </div>
              <div className="flex justify-between">
                <span>Database Integrity:</span>
                <span>{metrics.databaseIntegrity}</span>
              </div>
            </div>
          </motion.div>
        )}

        <motion.div
          className="bg-white bg-opacity-10 p-6 rounded-lg shadow-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          <h2 className="text-2xl font-semibold mb-4">Committee Members</h2>
          <ul className="space-y-2">
            {committeeMembers.map((member, index) => (
              <li key={index} className="flex justify-between">
                <span>{member.name}</span>
                <span>{member.role}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      </div>
    </div>
  );
};

export default SystemSoulPage;