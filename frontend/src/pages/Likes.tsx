import React, { useEffect, useLayoutEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useFeedback } from '../hooks/useFeedback';
import { setupScrollListener, getScrollPosition } from '../utils/scrollManager';
import { PaperCard } from '../components/Paper/PaperCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import apiClient from '../api/client';
import type { Paper } from '../types/paper';
import './Likes.css';

const ROUTE = '/likes';

export const Likes: React.FC = () => {
  const location = useLocation();
  const { feedback, unlike } = useFeedback();
  const likedIds = feedback.liked;

  // Fetch full paper details for liked paper IDs
  const { data: papers, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['liked-papers', likedIds],
    queryFn: async () => {
      if (!likedIds || likedIds.length === 0) {
        return [];
      }

      console.log('Fetching liked papers:', likedIds.length);
      
      // Use bulk endpoint to fetch all papers at once
      const { data } = await apiClient.get('/api/papers/bulk/by-ids', {
        params: {
          paper_ids: likedIds.join(','),
        },
      });
      
      console.log('Fetched liked papers:', data?.length || 0);
      return data || [];
    },
    enabled: likedIds.length > 0,
    staleTime: 30 * 1000, // 30 seconds
  });

  // Handle unlike
  const handleUnlike = (paper: Paper) => {
    console.log('Unliking paper:', paper.paperId);
    unlike(paper.paperId);
    // Refetch after a short delay to update the list
    setTimeout(() => {
      refetch();
    }, 500);
  };

  // Restore scroll position immediately on mount (before paint)
  useLayoutEffect(() => {
    if (location.pathname === ROUTE) {
      const savedPosition = getScrollPosition(ROUTE);
      if (savedPosition !== null && savedPosition > 0) {
        // Restore immediately to prevent visible jump
        window.scrollTo(0, savedPosition);
      }
    }
  }, [location.pathname]);

  // Also restore after papers load to handle cases where content height changes
  useEffect(() => {
    if (location.pathname === ROUTE && papers && papers.length > 0) {
      const savedPosition = getScrollPosition(ROUTE);
      if (savedPosition !== null && savedPosition > 0) {
        // Use double requestAnimationFrame to ensure DOM is fully rendered
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            window.scrollTo(0, savedPosition);
          });
        });
      }
    }
  }, [location.pathname, papers]);

  // Setup scroll listener to save position
  useEffect(() => {
    if (location.pathname === ROUTE) {
      const cleanup = setupScrollListener(ROUTE);
      return cleanup;
    }
  }, [location.pathname]);

  // Get like status (should always be 'liked' for papers on this page)
  const getLikeStatus = (paperId: string): 'liked' | 'disliked' | null => {
    if (feedback.liked.includes(paperId)) return 'liked';
    return null;
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="likes-page">
        <div className="likes-header">
          <h1>Liked Papers</h1>
          <p className="likes-subtitle">Your collection of favorite research papers</p>
        </div>
        <div className="papers-container">
          <LoadingSpinner text="Loading your liked papers..." />
        </div>
      </div>
    );
  }

  // Show error state
  if (isError) {
    return (
      <div className="likes-page">
        <div className="likes-header">
          <h1>Liked Papers</h1>
          <p className="likes-subtitle">Your collection of favorite research papers</p>
        </div>
        <div className="papers-container">
          <ErrorMessage
            message={
              (error as any)?.response?.data?.detail ||
              error?.message ||
              'Failed to load liked papers. Please try again.'
            }
            onRetry={() => refetch()}
          />
        </div>
      </div>
    );
  }

  // Show empty state
  if (!papers || papers.length === 0) {
    return (
      <div className="likes-page">
        <div className="likes-header">
          <h1>Liked Papers</h1>
          <p className="likes-subtitle">Your collection of favorite research papers</p>
        </div>
        <div className="papers-container">
          <div className="empty-state">
            <p>You haven't liked any papers yet.</p>
            <p className="empty-state-hint">Start exploring papers and like the ones you find interesting!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="likes-page">
      <div className="likes-header">
        <h1>Liked Papers</h1>
        <p className="likes-subtitle">
          Your collection of {papers.length} favorite research paper{papers.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="papers-container">
        <div className="papers-list">
          {papers.map((paper: Paper) => (
            <PaperCard
              key={paper.paperId}
              paper={paper}
              likeStatus={getLikeStatus(paper.paperId)}
              onLike={() => handleUnlike(paper)}
              onDislike={() => {}} // Disable dislike on likes page
            />
          ))}
        </div>
      </div>
    </div>
  );
};
