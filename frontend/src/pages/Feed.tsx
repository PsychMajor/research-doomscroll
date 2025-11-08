import React, { useState, useEffect, useRef, useCallback } from 'react';
import { usePapers } from '../hooks/usePapers';
import { useFeedback } from '../hooks/useFeedback';
import { PaperCard } from '../components/Paper/PaperCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import type { Paper } from '../types/paper';
import './Feed.css';

export const Feed: React.FC = () => {
  const [topics, setTopics] = useState('');
  const [authors, setAuthors] = useState('');
  const [sortBy, setSortBy] = useState<'recency' | 'relevance'>('recency');
  const [activeSearch, setActiveSearch] = useState<{ topics: string; authors: string; sortBy: 'recency' | 'relevance' } | null>(null);
  
  const observerTarget = useRef<HTMLDivElement>(null);
  const { useSearchPapers } = usePapers();
  const { feedback, like, unlike, dislike, undislike } = useFeedback();

  const {
    data,
    isLoading,
    isError,
    error,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useSearchPapers(activeSearch);

  // Handle search
  const handleSearch = () => {
    if (topics || authors) {
      setActiveSearch({
        topics,
        authors,
        sortBy,
      });
    }
  };

  // Handle Enter key in inputs
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle like/unlike
  const handleLike = (paper: Paper) => {
    const isLiked = feedback.liked.includes(paper.paperId);
    if (isLiked) {
      unlike(paper.paperId);
    } else {
      like({ paperId: paper.paperId, paperData: paper });
    }
  };

  // Handle dislike/undislike
  const handleDislike = (paper: Paper) => {
    const isDisliked = feedback.disliked.includes(paper.paperId);
    if (isDisliked) {
      undislike(paper.paperId);
    } else {
      dislike({ paperId: paper.paperId, paperData: paper });
    }
  };

  // Get like status for a paper
  const getLikeStatus = (paperId: string): 'liked' | 'disliked' | null => {
    if (feedback.liked.includes(paperId)) return 'liked';
    if (feedback.disliked.includes(paperId)) return 'disliked';
    return null;
  };

  // Infinite scroll observer
  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const [target] = entries;
    if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  useEffect(() => {
    const element = observerTarget.current;
    if (!element) return;

    const option = { threshold: 0 };
    const observer = new IntersectionObserver(handleObserver, option);
    observer.observe(element);

    return () => observer.unobserve(element);
  }, [handleObserver]);

  // Flatten all papers from all pages
  const allPapers = data?.pages.flat() ?? [];

  return (
    <div className="feed-page">
      <div className="feed-header">
        <h1>Research Feed</h1>
        <p className="feed-subtitle">Discover papers tailored to your interests</p>
      </div>

      <div className="search-section">
        <div className="search-form">
          <div className="search-inputs">
            <input
              type="text"
              placeholder="Topics (comma-separated)..."
              className="search-input"
              value={topics}
              onChange={(e) => setTopics(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <input
              type="text"
              placeholder="Authors (comma-separated)..."
              className="search-input"
              value={authors}
              onChange={(e) => setAuthors(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>
          <div className="search-controls">
            <select
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'recency' | 'relevance')}
            >
              <option value="recency">Most Recent</option>
              <option value="relevance">Most Relevant</option>
            </select>
            <button 
              className="search-btn"
              onClick={handleSearch}
              disabled={!topics && !authors}
            >
              Search
            </button>
          </div>
        </div>
      </div>

      <div className="papers-container">
        {!activeSearch && (
          <div className="empty-state">
            <p>👆 Enter topics or authors above to start discovering papers</p>
          </div>
        )}

        {activeSearch && isLoading && (
          <LoadingSpinner text="Searching papers..." />
        )}

        {activeSearch && isError && (
          <ErrorMessage 
            message={error?.message || 'Failed to fetch papers'}
            onRetry={handleSearch}
          />
        )}

        {activeSearch && !isLoading && allPapers.length === 0 && (
          <div className="empty-state">
            <p>No papers found. Try different search terms.</p>
          </div>
        )}

        {allPapers.length > 0 && (
          <div className="papers-list">
            {allPapers.map((paper) => (
              <PaperCard 
                key={paper.paperId} 
                paper={paper}
                likeStatus={getLikeStatus(paper.paperId)}
                onLike={() => handleLike(paper)}
                onDislike={() => handleDislike(paper)}
              />
            ))}
          </div>
        )}

        {isFetchingNextPage && (
          <LoadingSpinner text="Loading more papers..." />
        )}

        {/* Intersection observer target for infinite scroll */}
        <div ref={observerTarget} style={{ height: '20px' }} />
      </div>
    </div>
  );
};
