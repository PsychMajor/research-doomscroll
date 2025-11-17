import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { ThemeProvider } from './contexts/ThemeContext';
import { Feed } from './pages/Feed';
import { Likes } from './pages/Likes';
import { Folders } from './pages/Folders';
import { FolderDetail } from './pages/FolderDetail';
import { SidePanel } from './components/Layout/SidePanel';
import { useAuth } from './hooks/useAuth';
import { createPersistedQueryClient, createQueryPersister, getPersistOptions } from './utils/queryCachePersister';
import { useState } from 'react';
import './App.css';

// Create persisted query client
const queryClient = createPersistedQueryClient();
const persister = createQueryPersister();
const persistOptions = getPersistOptions(persister);

function AppContent() {
  const location = useLocation();
  const { user, login, logout } = useAuth();
  const [isSidePanelOpen, setIsSidePanelOpen] = useState(false);

  return (
    <>
      <header className="app-header">
        <nav className="header-nav">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            aria-label="Search"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </Link>
          <Link 
            to="/folders" 
            className={`nav-link ${location.pathname === '/folders' ? 'active' : ''}`}
            aria-label="Folders"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2z"></path>
            </svg>
          </Link>
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            aria-label="Home"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </Link>
          <Link 
            to="/contact" 
            className={`nav-link ${location.pathname === '/contact' ? 'active' : ''}`}
            aria-label="Help"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </Link>
          <button 
            className="nav-menu-btn"
            onClick={() => setIsSidePanelOpen(true)}
            aria-label="Open menu"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </button>
        </nav>
      </header>
      
      <SidePanel
        isOpen={isSidePanelOpen}
        onClose={() => setIsSidePanelOpen(false)}
        user={user}
        onLogin={login}
        onLogout={logout}
      />
      
      <div className="app">
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Feed />} />
            <Route path="/likes" element={<Likes />} />
            <Route path="/folders" element={<Folders />} />
            <Route path="/folders/:folderId" element={<FolderDetail />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </>
  );
}

function App() {
  return (
    <ThemeProvider>
      <PersistQueryClientProvider
        client={queryClient}
        persistOptions={persistOptions}
      >
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </PersistQueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
