import React, { useState, useEffect, useLayoutEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useFolders } from '../hooks/useFolders';
import { setupScrollListener, getScrollPosition } from '../utils/scrollManager';
import { FolderCard } from '../components/Folder/FolderCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import './Folders.css';

const ROUTE = '/folders';

export const Folders: React.FC = () => {
  const location = useLocation();
  const { useFoldersList, useCreateFolder, useDeleteFolder } = useFolders();
  const { data: folders, isLoading, isError, error, refetch } = useFoldersList();
  const createFolderMutation = useCreateFolder();
  const deleteFolderMutation = useDeleteFolder();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  // Restore scroll position immediately on mount (before paint)
  useLayoutEffect(() => {
    if (location.pathname === ROUTE) {
      const savedPosition = getScrollPosition(ROUTE);
      if (savedPosition !== null && savedPosition > 0) {
        window.scrollTo(0, savedPosition);
      }
    }
  }, [location.pathname]);

  // Setup scroll listener to save position
  useEffect(() => {
    if (location.pathname === ROUTE) {
      const cleanup = setupScrollListener(ROUTE);
      return cleanup;
    }
  }, [location.pathname]);

  // Handle create folder
  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    try {
      await createFolderMutation.mutateAsync({ name: newFolderName.trim() });
      setNewFolderName('');
      setShowCreateModal(false);
    } catch (error) {
      console.error('Error creating folder:', error);
    }
  };

  // Handle delete folder
  const handleDeleteFolder = (folderId: string) => {
    if (folderId === 'likes') {
      alert('Cannot delete the Likes folder');
      return;
    }

    if (!confirm('Are you sure you want to delete this folder? All papers in it will be removed.')) {
      return;
    }

    // Use mutate instead of mutateAsync for optimistic updates
    deleteFolderMutation.mutate(folderId, {
      onError: (error) => {
        console.error('Error deleting folder:', error);
        alert('Failed to delete folder. Please try again.');
      },
    });
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="folders-page">
        <div className="folders-header-bubble">
          <div className="folders-header-content">
            <h1 className="folders-title">My Folders</h1>
            <p className="folders-subtitle">Organize your research papers into collections</p>
          </div>
        </div>
        <div className="folders-container">
          <LoadingSpinner text="Loading your folders..." />
        </div>
      </div>
    );
  }

  // Show error state
  if (isError) {
    return (
      <div className="folders-page">
        <div className="folders-header-bubble">
          <div className="folders-header-content">
            <h1 className="folders-title">My Folders</h1>
            <p className="folders-subtitle">Organize your research papers into collections</p>
          </div>
        </div>
        <div className="folders-container">
          <ErrorMessage
            message={
              (error as any)?.response?.data?.detail ||
              error?.message ||
              'Failed to load folders. Please try again.'
            }
            onRetry={() => refetch()}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="folders-page">
      <div className="folders-header-bubble">
        <div className="folders-header-content">
          <h1 className="folders-title">My Folders</h1>
          <p className="folders-subtitle">Organize your research papers into collections</p>
        </div>
        <button
          className="create-folder-btn"
          onClick={() => setShowCreateModal(true)}
        >
          + Create New Folder
        </button>
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Folder</h2>
            <input
              type="text"
              placeholder="Folder name"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleCreateFolder();
                }
              }}
              className="folder-name-input"
              autoFocus
            />
            <div className="modal-actions">
              <button
                onClick={handleCreateFolder}
                className="modal-btn primary"
                disabled={!newFolderName.trim() || createFolderMutation.isPending}
              >
                {createFolderMutation.isPending ? 'Creating...' : 'Create'}
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setNewFolderName('');
                }}
                className="modal-btn secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="folders-container">
        {!folders || folders.length === 0 ? (
          <div className="empty-state">
            <p>You don't have any folders yet.</p>
            <p className="empty-state-hint">Create a folder to organize your papers, or like papers to add them to your Likes folder!</p>
          </div>
        ) : (
          <div className="folders-grid">
            {folders.map((folder) => (
              <FolderCard
                key={folder.id}
                folder={folder}
                onDelete={handleDeleteFolder}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
