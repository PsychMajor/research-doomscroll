import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/Layout/Header';
import { Feed } from './pages/Feed';
import { Likes } from './pages/Likes';
import { Folders } from './pages/Folders';
import { FolderDetail } from './pages/FolderDetail';
import { useAuth } from './hooks';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30 * 1000, // 30 seconds
    },
  },
});

function AppContent() {
  const { isAuthenticated, logout } = useAuth();

  // Get user info from profile query when authenticated
  const user = isAuthenticated ? { name: 'User' } : null;

  return (
    <div className="app">
      <Header user={user} onLogout={logout} />
      
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
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
