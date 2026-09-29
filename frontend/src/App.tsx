import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { ChatWorkspace } from './pages/ChatWorkspace';
import { Search } from './pages/Search';
import { ImageAnalysis } from './pages/ImageAnalysis';
import { PerformanceDashboard } from './pages/PerformanceDashboard';
import { PrivacyDashboard } from './pages/PrivacyDashboard';
import { Settings } from './pages/Settings';
import { type DocumentItem, type WorkspaceStats, api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [selectedDocIdForChat, setSelectedDocIdForChat] = useState<string | undefined>(undefined);
  const [isNpuActive, setIsNpuActive] = useState<boolean>(false);

  const refreshWorkspace = async () => {
    try {
      const [docs, st, perf] = await Promise.all([
        api.listDocuments(),
        api.getStats(),
        api.getPerformanceMetrics(),
      ]);
      setDocuments(docs);
      setStats(st);
      setIsNpuActive(perf.hardware.npu_telemetry.is_hardware_npu_active);
    } catch (err) {
      console.error('Workspace refresh failed', err);
    }
  };

  useEffect(() => {
    refreshWorkspace();
  }, []);

  const handleNavigateToChat = (docId?: string) => {
    setSelectedDocIdForChat(docId);
    setActiveTab('workspace');
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-red-500/30 selection:text-red-200">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        onNavigate={setActiveTab}
        isNpuActive={isNpuActive}
      />

      {/* Main Workspace Frame */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onNavigate={setActiveTab}
          documentCount={documents.length}
          totalQueries={stats ? stats.total_queries : 0}
        />

        {/* Content Viewport */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-gradient-to-b from-slate-950 via-slate-900/30 to-slate-950">
          {activeTab === 'dashboard' && (
            <Dashboard
              stats={stats}
              documents={documents}
              onNavigate={setActiveTab}
              onRefreshDocs={refreshWorkspace}
            />
          )}

          {activeTab === 'documents' && (
            <Documents
              documents={documents}
              onRefresh={refreshWorkspace}
              onNavigateToChat={handleNavigateToChat}
            />
          )}

          {activeTab === 'workspace' && (
            <ChatWorkspace
              documents={documents}
              selectedDocId={selectedDocIdForChat}
              onSelectDocId={setSelectedDocIdForChat}
            />
          )}

          {activeTab === 'search' && (
            <Search onNavigateToChat={handleNavigateToChat} />
          )}

          {activeTab === 'images' && <ImageAnalysis />}

          {activeTab === 'performance' && <PerformanceDashboard />}

          {activeTab === 'privacy' && <PrivacyDashboard />}

          {activeTab === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  );
};

export default App;
