import React, { useState, useEffect, useLayoutEffect, useRef, useCallback, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { usePapers } from '../hooks/usePapers';
import { useFeedback } from '../hooks/useFeedback';
import { useProfile } from '../hooks/useProfile';
import { useAuth } from '../hooks';
import { useFeedCache, getFeedState, getFormState } from '../hooks/useFeedCache';
import { setupScrollListener, getScrollPosition } from '../utils/scrollManager';
import { PaperCard } from '../components/Paper/PaperCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import { FolderModal } from '../components/Folder/FolderModal';
import { useFolders } from '../hooks/useFolders';
import type { Paper } from '../types/paper';
import './Feed.css';

const ROUTE = '/';

export const Feed: React.FC = () => {
  const location = useLocation();
  const containerRef = useRef<HTMLDivElement>(null);
  const observerTarget = useRef<HTMLDivElement>(null);
  
  // Feed cache for state persistence
  const { cachedState, cachedForm, saveState, saveForm } = useFeedCache();
  
  
  // Initialize state from cache or defaults
  // Use lazy initialization to ensure cache is read synchronously
  const [topics, setTopics] = useState(() => {
    const form = getFormState();
    return form?.topics || '';
  });
  const [authors, setAuthors] = useState(() => {
    const form = getFormState();
    return form?.authors || '';
  });
  const [sortBy, setSortBy] = useState<'recency' | 'relevance'>(() => {
    const form = getFormState();
    return form?.sortBy || 'recency';
  });
  
  // Get initial search from cache synchronously
  const getInitialSearchSync = (): { topics: string; authors: string; sortBy: 'recency' | 'relevance' } | null => {
    const state = getFeedState();
    if (state?.activeSearch) {
      const search = state.activeSearch;
      if (search.topics || search.authors) {
        return {
          topics: search.topics || '',
          authors: search.authors || '',
          sortBy: search.sortBy || 'recency',
        };
      }
    }
    return null;
  };
  
  const [activeSearch, setActiveSearch] = useState<{ topics: string; authors: string; sortBy: 'recency' | 'relevance' } | null>(
    () => getInitialSearchSync()
  );
  
  const { useSearchPapers, useSearchPapersByQuery } = usePapers();
  const { feedback, like, unlike, dislike, undislike, isLoading: feedbackLoading } = useFeedback();
  const { useUpdateProfile } = useProfile();
  const { isAuthenticated } = useAuth();
  const updateProfileMutation = useUpdateProfile();
  
  // Unified search query state - restore from cache if available
  const [unifiedQuery, setUnifiedQuery] = useState(() => {
    const state = getFeedState();
    return state?.unifiedSearchQuery || '';
  });
  const [searchQuery, setSearchQuery] = useState(() => {
    const state = getFeedState();
    return state?.useUnifiedSearch && state?.unifiedSearchQuery ? state.unifiedSearchQuery : '';
  }); // The actual query to search (set on button click)
  const [useUnifiedSearch, setUseUnifiedSearch] = useState(() => {
    const state = getFeedState();
    return state?.useUnifiedSearch || false;
  });

  // Track feedback state at the start of each search to only filter papers that were already liked/passed
  const [feedbackAtSearchStart, setFeedbackAtSearchStart] = useState<{
    liked: string[];
    disliked: string[];
  }>({ liked: [], disliked: [] });
  

  // Always call both hooks (React rules - hooks must be called unconditionally)
  // Only search when searchQuery is set (on button click), not when unifiedQuery changes
  const queryForSearch = useUnifiedSearch && searchQuery ? searchQuery : null;
  
  const unifiedSearchData = useSearchPapersByQuery(
    queryForSearch,
    sortBy
  );
  
  const regularSearchData = useSearchPapers(activeSearch);
  
  // Use unified search data if unified search is active, otherwise use regular search
  const searchData = useUnifiedSearch ? unifiedSearchData : regularSearchData;
  const {
    data,
    isLoading,
    isError,
    error,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = searchData;

  // Restore scroll position immediately on mount (before paint)
  // useLayoutEffect runs synchronously before browser paints, preventing visible jump
  useLayoutEffect(() => {
    if (location.pathname === ROUTE) {
      const savedPosition = getScrollPosition(ROUTE);
      if (savedPosition !== null && savedPosition > 0) {
        // Restore immediately to prevent visible jump
        window.scrollTo(0, savedPosition);
      }
    }
  }, [location.pathname]);

  // Also restore after data loads to handle cases where content height changes
  useEffect(() => {
    if (location.pathname === ROUTE && data && data.pages.length > 0) {
      const savedPosition = getScrollPosition(ROUTE);
      if (savedPosition !== null && savedPosition > 0) {
        // Use a small delay to ensure DOM is fully rendered
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            window.scrollTo(0, savedPosition);
          });
        });
      }
    }
  }, [location.pathname, data]);

  // Setup scroll listener to save position
  useEffect(() => {
    if (location.pathname === ROUTE) {
      const cleanup = setupScrollListener(ROUTE);
      return cleanup;
    }
  }, [location.pathname]);

  // Save form state when it changes
  useEffect(() => {
    saveForm({ topics, authors, sortBy });
  }, [topics, authors, sortBy, saveForm]);

  // Save active search state when it changes
  useEffect(() => {
    if (activeSearch) {
      saveState({ activeSearch });
    }
  }, [activeSearch, saveState]);

  // Restore form state from cache when it becomes available
  useEffect(() => {
    if (cachedForm) {
      // Only restore if current values are empty (to avoid overwriting user input)
      if (!topics && !authors && (cachedForm.topics || cachedForm.authors)) {
        setTopics(cachedForm.topics);
        setAuthors(cachedForm.authors);
        setSortBy(cachedForm.sortBy);
      }
    }
  }, [cachedForm]); // Run when cachedForm changes

  // Restore unified search state from cache when navigating back
  useEffect(() => {
    if (location.pathname === ROUTE && cachedState) {
      // Restore unified search if it was active
      if (cachedState.useUnifiedSearch && cachedState.unifiedSearchQuery) {
        if (!useUnifiedSearch || searchQuery !== cachedState.unifiedSearchQuery) {
          setSearchQuery(cachedState.unifiedSearchQuery);
          setUseUnifiedSearch(true);
          setUnifiedQuery(cachedState.unifiedSearchQuery);
          setActiveSearch(null); // Clear activeSearch when using unified search
        }
      }
    }
  }, [location.pathname, cachedState]); // Run when route or cache changes

  // Restore active search from cache when it becomes available
  // This needs to run early to ensure React Query can use cached data
  // BUT: Don't restore if we're using unified search
  useEffect(() => {
    if (location.pathname === ROUTE && cachedState?.activeSearch && !useUnifiedSearch) {
      const search = cachedState.activeSearch;
      if (search.topics || search.authors) {
        const restored = {
          topics: search.topics || '',
          authors: search.authors || '',
          sortBy: search.sortBy || 'recency',
        };
        
        // Only restore if we don't have an active search or if it's different
        if (!activeSearch) {
          console.log('Restoring active search from cache:', restored);
          setActiveSearch(restored);
        } else {
          // Check if the restored search is different from current
          const currentKey = `${activeSearch.topics}|${activeSearch.authors}|${activeSearch.sortBy}`;
          const restoredKey = `${restored.topics}|${restored.authors}|${restored.sortBy}`;
          if (currentKey !== restoredKey) {
            console.log('Restoring different active search from cache:', restored);
            setActiveSearch(restored);
          }
        }
      }
    }
  }, [cachedState, location.pathname, activeSearch, useUnifiedSearch]); // Run when cachedState or route changes

  // Log query state changes (only on significant changes)
  useEffect(() => {
    if (isError || (data && data.pages && data.pages.length > 0)) {
      console.log('Query State:', {
        activeSearch,
        isLoading,
        isError,
        error: error?.message,
        hasData: !!data,
        pagesCount: data?.pages?.length || 0,
        totalPapers: data?.pages?.flat().length || 0,
      });
    }
  }, [isError, data?.pages?.length]); // Only log on errors or when we get data

  // Track if we've captured feedback for the current search
  const [hasCapturedFeedback, setHasCapturedFeedback] = useState(false);
  const previousSearchKeyRef = useRef<string>('');

  // Update feedback state at search start whenever activeSearch changes
  // Only capture when search key actually changes, not when feedback changes
  useEffect(() => {
    if (activeSearch) {
      const searchKey = `${activeSearch.topics}|${activeSearch.authors}|${activeSearch.sortBy}`;
      
      // If this is a new search (different key), reset flag
      if (searchKey !== previousSearchKeyRef.current) {
        previousSearchKeyRef.current = searchKey;
        setHasCapturedFeedback(false); // Reset flag for new search
      }
    }
  }, [activeSearch]); // Only update when search changes

  // Capture feedback when search changes AND feedback is loaded
  // OR when feedback finishes loading for the first time (for page reloads)
  useEffect(() => {
    if (activeSearch && !feedbackLoading && !hasCapturedFeedback) {
      setFeedbackAtSearchStart({
        liked: [...feedback.liked],
        disliked: [...feedback.disliked],
      });
      setHasCapturedFeedback(true);
      console.log('Captured feedback for search:', {
        liked: feedback.liked.length,
        disliked: feedback.disliked.length,
        searchKey: `${activeSearch.topics}|${activeSearch.authors}|${activeSearch.sortBy}`,
      });
    }
  }, [activeSearch, feedbackLoading, hasCapturedFeedback]); // Only update when search/loading changes, NOT when feedback content changes

  // Handle unified search (only triggered on button click)
  const handleUnifiedSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedQuery = unifiedQuery.trim();
    
    if (!trimmedQuery) {
      return;
    }
    
    // Capture feedback state right before starting new search
    if (!feedbackLoading) {
      setFeedbackAtSearchStart({
        liked: [...feedback.liked],
        disliked: [...feedback.disliked],
      });
      setHasCapturedFeedback(true);
    }
    
    // Set the search query (this triggers the actual search)
    // Clear activeSearch FIRST to prevent cache restoration from interfering
    setActiveSearch(null);
    // Then set unified search state
    setSearchQuery(trimmedQuery);
    setUseUnifiedSearch(true);
    
    // Save unified search state to cache
    saveState({
      unifiedSearchQuery: trimmedQuery,
      useUnifiedSearch: true,
      activeSearch: null, // Clear activeSearch when using unified search
    });
    
    // Scroll to first card, accounting for nav bar
    // Wait a bit for the DOM to update with the new papers
    setTimeout(() => {
      const firstCard = document.querySelector('.paper-card');
      if (firstCard) {
        const navBarHeight = 80; // Approximate nav bar height with padding
        const cardPosition = firstCard.getBoundingClientRect().top + window.pageYOffset;
        const scrollPosition = cardPosition - navBarHeight - 20; // 20px extra padding
        window.scrollTo({ top: Math.max(0, scrollPosition), behavior: 'smooth' });
      } else {
        // Fallback to top if no cards yet
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 100);
  };
  
  // Handle clear button - only clear the input, don't reset search state
  const handleClear = () => {
    setUnifiedQuery('');
    // Don't clear searchQuery or useUnifiedSearch - let user see results while typing new query
  };
  
  // Handle search and save profile
  const handleSearch = async () => {
    console.log('Search triggered:', { topics, authors, sortBy });
    
    if (!topics && !authors) {
      console.warn('Search attempted without topics or authors');
      return;
    }
    
    // Switch to regular search mode
    setUseUnifiedSearch(false);
    setSearchQuery(''); // Clear unified search query
    
    // Save state to cache - clear unified search
    saveState({
      useUnifiedSearch: false,
      unifiedSearchQuery: '',
    });

    // Parse topics and authors from comma-separated strings to arrays
    const topicsArray = topics
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);
    
    const authorsArray = authors
      .split(',')
      .map(a => a.trim())
      .filter(a => a.length > 0);

    // Save profile if user is authenticated
    if (isAuthenticated) {
      try {
        console.log('Saving profile:', { topics: topicsArray, authors: authorsArray });
        await updateProfileMutation.mutateAsync({
          topics: topicsArray,
          authors: authorsArray,
        });
        console.log('Profile saved successfully');
      } catch (error) {
        console.error('Error saving profile:', error);
        // Continue with search even if profile save fails
      }
    }

    // Trigger search
    const searchParams = {
      topics,
      authors,
      sortBy,
    };
    console.log('Setting active search:', searchParams);
    
    // Capture feedback state right before starting new search
    // This ensures we have the latest feedback state before filtering
    if (!feedbackLoading) {
      setFeedbackAtSearchStart({
        liked: [...feedback.liked],
        disliked: [...feedback.disliked],
      });
      console.log('Captured feedback before new search:', {
        liked: feedback.liked.length,
        disliked: feedback.disliked.length,
      });
    }
    
    setActiveSearch(searchParams);
    
    // Scroll to first card, accounting for nav bar
    // Wait a bit for the DOM to update with the new papers
    setTimeout(() => {
      const firstCard = document.querySelector('.paper-card');
      if (firstCard) {
        const navBarHeight = 80; // Approximate nav bar height with padding
        const cardPosition = firstCard.getBoundingClientRect().top + window.pageYOffset;
        const scrollPosition = cardPosition - navBarHeight - 20; // 20px extra padding
        window.scrollTo({ top: Math.max(0, scrollPosition), behavior: 'smooth' });
      } else {
        // Fallback to top if no cards yet
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 100);
  };

  // Handle Enter key in inputs
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // State for showing authentication error
  const [authError, setAuthError] = useState<string | null>(null);

  // Clear auth error after 5 seconds
  useEffect(() => {
    if (authError) {
      const timer = setTimeout(() => setAuthError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [authError]);

  // Handle like/unlike
  const handleLike = (paper: Paper) => {
    if (!isAuthenticated) {
      setAuthError('Please log in to like articles');
      return;
    }

    const isLiked = feedback.liked.includes(paper.paperId);
    console.log(`${isLiked ? 'Unlike' : 'Like'} paper:`, paper.paperId);
    if (isLiked) {
      unlike(paper.paperId);
    } else {
      like({ paperId: paper.paperId, paperData: paper });
    }
  };

  // Handle dislike/undislike
  const handleDislike = (paper: Paper) => {
    if (!isAuthenticated) {
      setAuthError('Please log in to pass articles');
      return;
    }

    const isDisliked = feedback.disliked.includes(paper.paperId);
    console.log(`${isDisliked ? 'Undislike' : 'Dislike'} paper:`, paper.paperId);
    if (isDisliked) {
      undislike(paper.paperId);
    } else {
      dislike({ paperId: paper.paperId, paperData: paper });
    }
  };

  // Folder modal state and handlers
  const [isFolderModalOpen, setIsFolderModalOpen] = useState(false);
  const [selectedPaperForFolder, setSelectedPaperForFolder] = useState<Paper | null>(null);
  
  const folders = useFolders();
  const { useFoldersList, useAddPaperToFolder, useCreateFolder } = folders;
  const { data: foldersList, refetch: refetchFolders } = useFoldersList();
  const addPaperToFolderMutation = useAddPaperToFolder();
  const createFolderMutation = useCreateFolder();

  const handleAddToFolder = (paperId: string) => {
    const paper = allPapers.find(p => p.paperId === paperId);
    if (paper) {
      setSelectedPaperForFolder(paper);
      setIsFolderModalOpen(true);
    }
  };

  const handleCloseFolderModal = () => {
    setIsFolderModalOpen(false);
    setSelectedPaperForFolder(null);
  };

  const handleSelectFolder = (folderId: string) => {
    if (!selectedPaperForFolder) return;
    
    // Only like the paper when adding to the "Likes" folder
    if (folderId === 'likes' && !feedback.liked.includes(selectedPaperForFolder.paperId)) {
      like({ paperId: selectedPaperForFolder.paperId, paperData: selectedPaperForFolder });
    }
    
    addPaperToFolderMutation.mutate({
      folderId,
      paperId: selectedPaperForFolder.paperId,
      paperData: selectedPaperForFolder,
    });
    handleCloseFolderModal();
  };

  const handleCreateFolder = async (name: string, description?: string) => {
    await createFolderMutation.mutateAsync({
      name,
      description,
    });
    // Refetch folders after creation to ensure the new folder appears
    await refetchFolders();
  };

  // Get like status for a paper
  const getLikeStatus = (paperId: string): 'liked' | 'disliked' | null => {
    if (feedback.liked.includes(paperId)) return 'liked';
    if (feedback.disliked.includes(paperId)) return 'disliked';
    return null;
  };

  // Check if a paper is in any folder
  const isPaperInFolder = (paperId: string): boolean => {
    if (!foldersList) return false;
    return foldersList.some(folder => 
      folder.papers && folder.papers.some((p: Paper) => p.paperId === paperId)
    );
  };

  // Infinite scroll observer
  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const [target] = entries;
    if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
      console.log('Infinite scroll triggered - fetching next page');
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
  const allPapers = useMemo(() => data?.pages.flat() ?? [], [data?.pages]);
  
  // Filter out papers that were already liked or passed BEFORE this search started
  // This way, papers you like/pass during the current session stay visible until next search
  // Memoize to prevent unnecessary recalculations
  const filteredPapers = useMemo(() => {
    return allPapers.filter(paper => {
      const wasLikedBeforeSearch = feedbackAtSearchStart.liked.includes(paper.paperId);
      const wasDislikedBeforeSearch = feedbackAtSearchStart.disliked.includes(paper.paperId);
      return !wasLikedBeforeSearch && !wasDislikedBeforeSearch;
    });
  }, [allPapers, feedbackAtSearchStart.liked, feedbackAtSearchStart.disliked]);
  
  useEffect(() => {
    if (allPapers.length > 0) {
      console.log('Total papers loaded:', allPapers.length);
      console.log('Filtered papers (excluding previously liked/passed):', filteredPapers.length);
      console.log('Feedback at search start:', {
        liked: feedbackAtSearchStart.liked.length,
        disliked: feedbackAtSearchStart.disliked.length,
      });
    }
  }, [allPapers.length, filteredPapers.length, feedbackAtSearchStart]);

  return (
    <div className="feed-page" ref={containerRef}>
      {/* Google-like Search Interface */}
      <div className="google-style-search-container">
        <div className="pando-logo-section">
          <h1 className="pando-logo">Pando</h1>
          <p className="pando-subtitle">Keep up with the world's literature</p>
        </div>
        
        <form 
          className="google-style-search-form"
          onSubmit={handleUnifiedSearch}
        >
          <div className="google-search-box">
            <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <input
              type="text"
              className="google-search-input"
              value={unifiedQuery}
              onChange={(e) => setUnifiedQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleUnifiedSearch(e as any);
                }
              }}
              placeholder="Search papers..."
              disabled={useUnifiedSearch && searchData.isFetching}
            />
          </div>
          
          <div className="google-search-buttons">
            <button 
              type="submit"
              className="google-search-btn"
              disabled={!unifiedQuery.trim() || (useUnifiedSearch && searchData.isFetching)}
            >
              {useUnifiedSearch && searchData.isFetching ? 'Searching...' : 'Search'}
            </button>
            <button 
              type="button"
              className="google-search-btn"
              onClick={handleClear}
            >
              Clear
            </button>
          </div>
        </form>
        
        {/* Advanced Options - Collapsed */}
        <details className="advanced-options-details">
          <summary className="advanced-options-summary">Advanced Options</summary>
          <div className="advanced-options-content">
            <div className="advanced-option-field">
              <label className="advanced-option-label">Sort By</label>
              <select
                className="advanced-option-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'recency' | 'relevance')}
              >
                <option value="recency">Recency (Newest First)</option>
                <option value="relevance">Relevance (Most Relevant)</option>
              </select>
            </div>
            
            <div className="advanced-search-section">
              <h3 className="advanced-search-title">Advanced Search (Topics & Authors)</h3>
              <form 
                className="advanced-search-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearch();
                }}
              >
                <div className="advanced-search-field">
                  <label className="advanced-search-label">Topics & Keywords</label>
                  <input
                    type="text"
                    placeholder="Pain, Spinal cord injury"
                    className="advanced-search-input"
                    value={topics}
                    onChange={(e) => setTopics(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                </div>

                <div className="advanced-search-field">
                  <label className="advanced-search-label">Authors</label>
                  <input
                    type="text"
                    placeholder="Michael J. Iadarola, Matthew R. Sapio"
                    className="advanced-search-input"
                    value={authors}
                    onChange={(e) => setAuthors(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                </div>

                <button 
                  type="submit"
                  className="advanced-search-btn"
                  disabled={(!topics && !authors) || updateProfileMutation.isPending}
                >
                  {updateProfileMutation.isPending ? 'Searching...' : 'Search'}
                </button>
              </form>
            </div>
          </div>
        </details>
      </div>

      {/* Papers Results - Only show when there are results */}
      {((useUnifiedSearch && searchQuery) || activeSearch) && (
      <div className="papers-container">
        {authError && (
          <div className="auth-error-banner">
            <span className="auth-error-icon">⚠</span>
            <span className="auth-error-text">{authError}</span>
          </div>
        )}

        {isLoading && (
          <LoadingSpinner text="Searching papers..." />
        )}

        {isError && (
          <ErrorMessage 
            message={
              (error as any)?.response?.data?.detail || 
              error?.message || 
              'Failed to fetch papers. Please check the console for details.'
            }
            onRetry={useUnifiedSearch ? handleUnifiedSearch : handleSearch}
          />
        )}

        {!isLoading && allPapers.length === 0 && ((useUnifiedSearch && searchQuery) || activeSearch) && (
          <div className="empty-state">
            <p>No papers found. Try different search terms.</p>
          </div>
        )}

        {!isLoading && allPapers.length > 0 && filteredPapers.length === 0 && (
          <div className="empty-state">
            <p>All papers in this search have been liked or passed. Try a new search!</p>
          </div>
        )}

        {filteredPapers.length > 0 && (
          <div className="papers-list">
            {filteredPapers.map((paper) => (
              <PaperCard 
                key={paper.paperId} 
                paper={paper}
                likeStatus={getLikeStatus(paper.paperId)}
                addedToFolder={isPaperInFolder(paper.paperId)}
                onLike={() => handleLike(paper)}
                onDislike={() => handleDislike(paper)}
                onAddToFolder={handleAddToFolder}
              />
            ))}
          </div>
        )}

        <FolderModal
          isOpen={isFolderModalOpen}
          onClose={handleCloseFolderModal}
          folders={foldersList || []}
          onSelectFolder={handleSelectFolder}
          onCreateFolder={handleCreateFolder}
        />

        {isFetchingNextPage && (
          <LoadingSpinner text="Loading more papers..." />
        )}

        {/* Intersection observer target for infinite scroll */}
        <div ref={observerTarget} style={{ height: '20px' }} />
      </div>
      )}
    </div>
  );
};
