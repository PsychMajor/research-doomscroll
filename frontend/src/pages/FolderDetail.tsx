import React, { useEffect, useLayoutEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useFolders } from '../hooks/useFolders';
import { useFeedback } from '../hooks/useFeedback';
import { setupScrollListener, getScrollPosition } from '../utils/scrollManager';
import { PaperCard } from '../components/Paper/PaperCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import type { Paper } from '../types/paper';
import './FolderDetail.css';

export const FolderDetail: React.FC = () => {
  const { folderId } = useParams<{ folderId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const route = `/folders/${folderId}`;

  const { useFolder, useRemovePaperFromFolder } = useFolders();
  const { data: folder, isLoading, isError, error, refetch } = useFolder(folderId || null);
  const removePaperMutation = useRemovePaperFromFolder();
  const { feedback, unlike } = useFeedback();

  // Restore scroll position immediately on mount (before paint)
  useLayoutEffect(() => {
    if (location.pathname === route) {
      const savedPosition = getScrollPosition(route);
      if (savedPosition !== null && savedPosition > 0) {
        window.scrollTo(0, savedPosition);
      }
    }
  }, [location.pathname, route]);

  // Also restore after papers load
  useEffect(() => {
    if (location.pathname === route && folder && folder.papers && folder.papers.length > 0) {
      const savedPosition = getScrollPosition(route);
      if (savedPosition !== null && savedPosition > 0) {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            window.scrollTo(0, savedPosition);
          });
        });
      }
    }
  }, [location.pathname, route, folder]);

  // Setup scroll listener to save position
  useEffect(() => {
    if (location.pathname === route) {
      const cleanup = setupScrollListener(route);
      return cleanup;
    }
  }, [location.pathname, route]);

  // Handle remove paper from folder
  const handleRemovePaper = (paperId: string) => {
    if (!folderId) return;

    // Use mutate instead of mutateAsync for non-blocking call
    // The optimistic update in onMutate will update the UI immediately
    removePaperMutation.mutate(
      {
        folderId,
        paperId,
      },
      {
        onSuccess: () => {
          // If removing from Likes folder, also unlike it
          if (folderId === 'likes' && feedback.liked.includes(paperId)) {
            unlike(paperId);
          }
        },
        onError: (error) => {
          console.error('Error removing paper from folder:', error);
        },
      }
    );
  };

  // Handle like/unlike (for Likes folder)
  const handleLike = (paper: Paper) => {
    if (folderId === 'likes') {
      // In Likes folder, like button should remove from folder
      handleRemovePaper(paper.paperId);
    }
  };

  // Get like status for a paper
  const getLikeStatus = (paperId: string): 'liked' | 'disliked' | null => {
    if (feedback.liked.includes(paperId)) return 'liked';
    if (feedback.disliked.includes(paperId)) return 'disliked';
    return null;
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="folder-detail-page">
        <div className="folder-detail-header">
          <button onClick={() => navigate('/folders')} className="back-btn">
            ← Back to Folders
          </button>
          <h1>Loading folder...</h1>
        </div>
        <div className="papers-container">
          <LoadingSpinner text="Loading papers in this folder..." />
        </div>
      </div>
    );
  }

  // Show error state
  if (isError || !folder) {
    return (
      <div className="folder-detail-page">
        <div className="folder-detail-header">
          <button onClick={() => navigate('/folders')} className="back-btn">
            ← Back to Folders
          </button>
          <h1>Folder</h1>
        </div>
        <div className="papers-container">
          <ErrorMessage
            message={
              (error as any)?.response?.data?.detail ||
              error?.message ||
              'Failed to load folder. Please try again.'
            }
            onRetry={() => refetch()}
          />
        </div>
      </div>
    );
  }

  const papers = folder.papers || [];

  return (
    <div className="folder-detail-page">
      <div className="folder-detail-header">
        <div className="header-top-row">
          <button onClick={() => navigate('/folders')} className="back-btn">
            ← Back to Folders
          </button>
          <div className="folder-paper-count-bubble">
            <p className="folder-paper-count">
              {papers.length} {papers.length === 1 ? 'paper' : 'papers'}
            </p>
          </div>
        </div>
        <div className="folder-title-bubble">
          <h1 className="folder-title">{folder.name}</h1>
        </div>
        {folder.description && (
          <p className="folder-description">{folder.description}</p>
        )}
      </div>

      <div className="papers-container">
        {papers.length === 0 ? (
          <div className="empty-state">
            <p>This folder is empty.</p>
            <p className="empty-state-hint">
              {folderId === 'likes'
                ? 'Like papers from the search page to add them here!'
                : 'Add papers to this folder to see them here.'}
            </p>
          </div>
        ) : (
          <div className="papers-list">
            {papers.map((paper: Paper) => (
              <PaperCard
                key={paper.paperId}
                paper={paper}
                likeStatus={getLikeStatus(paper.paperId)}
                onLike={folderId === 'likes' ? () => handleLike(paper) : undefined}
                onDislike={undefined} // Disable dislike on folder pages
                onRemove={folderId === 'likes' ? (paperId: string) => handleRemovePaper(paperId) : undefined}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
