import { useState } from 'react';
import Layout from './components/Layout';
import { ChatContainer } from './components/Chat/ChatContainer';
import { DashboardContainer } from './components/Dashboard/DashboardContainer';
import SCP from './pages/SCP';
import Observability from './pages/Observability';

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard' | 'scp' | 'observability'>('chat');

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {activeTab === 'chat' && <ChatContainer />}
      {activeTab === 'dashboard' && <DashboardContainer />}
      {activeTab === 'scp' && <SCP />}
      {activeTab === 'observability' && <Observability />}
    </Layout>
  );
}

export default App;
