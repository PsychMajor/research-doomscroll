import React, { useState, useEffect, useRef, useCallback } from 'react';
import { usePapers } from '../hooks/usePapers';
import { PaperCard } from '../components/Paper/PaperCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import './Feed.css';

export const Feed: React.FC = () => {
  const [topics, setTopics] = useState('');
  const [authors, setAuthors] = useState('');
  const [sortBy, setSortBy] = useState<'recency' | 'relevance'>('recency');
  const [searchTriggered, setSearchTriggered] = useState(false);
  const [page, setPage] = useState(1);
  
  const observerTarget = useRef<HTMLDivElement>(null);
  const { useSearchPapers } = usePapers();

  // Build search params
  const searchParams = searchTriggered && (topics || authors) ? {
    topics,
    authors,
    sortBy,
    page,
  } : null;

  const {
    data,
    isLoading,
    isError,
    error,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useSearchPapers(searchParams || { topics: '', authors: '', sortBy, page: 1 });

  // Handle search
  const handleSearch = () => {
    setPage(1);
    setSearchTriggered(true);
  };

  // Handle Enter key in inputs
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Infinite scroll observer
  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const [target] = entries;
    if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
      setPage(prev => prev + 1);
    }
  }, [hasNextPage, isFetchingNextPage]);

  useEffect(() => {
    const element = observerTarget.current;
    if (!element) return;

    const option = { threshold: 0 };
    const observer = new IntersectionObserver(handleObserver, option);
    observer.observe(element);

    return () => observer.unobserve(element);
  }, [handleObserver]);

  // Trigger fetchNextPage when page changes
  useEffect(() => {
    if (page > 1 && searchTriggered) {
      fetchNextPage();
    }
  }, [page, searchTriggered, fetchNextPage]);

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
        {!searchTriggered && (
          <div className="empty-state">
            <p>👆 Enter topics or authors above to start discovering papers</p>
          </div>
        )}

        {searchTriggered && isLoading && (
          <LoadingSpinner text="Searching papers..." />
        )}

        {searchTriggered && isError && (
          <ErrorMessage 
            message={error?.message || 'Failed to fetch papers'}
            onRetry={handleSearch}
          />
        )}

        {searchTriggered && !isLoading && allPapers.length === 0 && (
          <div className="empty-state">
            <p>No papers found. Try different search terms.</p>
          </div>
        )}

        {allPapers.length > 0 && (
          <div className="papers-list">
            {allPapers.map((paper) => (
              <PaperCard key={paper.paperId} paper={paper} />
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
