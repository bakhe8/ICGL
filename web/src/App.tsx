import React from 'react';
import TechnicalCapabilities from './components/TechnicalCapabilities';
import SystemSoulPage from './routes/SystemSoulPage';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<'technical' | 'soul'>('technical');

  return (
    <div className="bg-slate-900 min-h-screen text-white">
      {/* Navigation Header */}
      <nav className="border-b border-slate-700 p-4 bg-slate-900 sticky top-0 z-50 flex justify-between items-center bg-opacity-95 backdrop-blur">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          ICGL Sovereign Cockpit
        </h1>
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('technical')}
            className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'technical'
              ? 'bg-slate-700 text-white font-medium'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
          >
            Technical Core
          </button>
          <button
            onClick={() => setActiveTab('soul')}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${activeTab === 'soul'
              ? 'bg-indigo-600 text-white font-medium shadow-lg shadow-indigo-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
          >
            <span>🔮</span> System Soul
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main>
        {activeTab === 'soul' ? (
          <SystemSoulPage />
        ) : (
          <div className="p-10">
            <h2 className="text-2xl text-white mb-6 border-b border-slate-800 pb-2">Technical Underpinnings</h2>
            <TechnicalCapabilities />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;