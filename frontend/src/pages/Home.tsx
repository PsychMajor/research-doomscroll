import React, { useState, useEffect, useRef } from 'react';
import { PaperCard } from '../components/Paper/PaperCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import { FolderModal } from '../components/Folder/FolderModal';
import { usePapers } from '../hooks/usePapers';
import { useFeedback } from '../hooks/useFeedback';
import { useFolders } from '../hooks/useFolders';
import { useFollows, useFollowEntity, useFollowedPapers } from '../hooks/useFollows';
import { EntitySearch } from '../components/Follow/EntitySearch';
import { FollowedEntitiesList } from '../components/Follow/FollowedEntitiesList';
import type { Paper } from '../types/paper';
import type { EntitySearchResult, EntityType } from '../api/entitySearch';
import './Home.css';

type TabType = 'following' | 'foryou';

const STORAGE_KEY_TAB = 'home_active_tab';
const STORAGE_KEY_SCROLL_FOLLOWING = 'home_scroll_following';
const STORAGE_KEY_SCROLL_FORYOU = 'home_scroll_foryou';

export const Home: React.FC = () => {
  // Restore active tab from sessionStorage
  const getInitialTab = (): TabType => {
    const saved = sessionStorage.getItem(STORAGE_KEY_TAB);
    return (saved === 'following' || saved === 'foryou') ? saved : 'foryou';
  };

  const [activeTab, setActiveTab] = useState<TabType>(getInitialTab);
  const scrollTimeoutRef = useRef<number | null>(null);
  const { feedback, like, dislike } = useFeedback();
  const { useFoldersList } = useFolders();
  const { useRecommendations } = usePapers();
  
  // Fetch folders
  const { data: foldersList } = useFoldersList();
  
  // Fetch recommendations for "For You" tab
  const { data: recommendations, isLoading: isLoadingRecommendations, isError: isErrorRecommendations, error: recommendationsError } = useRecommendations(50);
  
  // Follow functionality
  const { data: follows } = useFollows();
  const followMutation = useFollowEntity();
  const { data: followedPapers, isLoading: isLoadingFollowedPapers, isError: isErrorFollowedPapers, error: followedPapersError } = useFollowedPapers(50, 200);
  
  // Folder functionality
  const [selectedPaperForFolder, setSelectedPaperForFolder] = useState<Paper | null>(null);
  const { useAddPaperToFolder, useCreateFolder, useFoldersList: useFoldersListForModal } = useFolders();
  const addPaperMutation = useAddPaperToFolder();
  const createFolderMutation = useCreateFolder();
  const { refetch: refetchFolders } = useFoldersListForModal();
  
  // Check if an entity is already being followed
  const isFollowing = (entityId: string, type: EntityType): boolean => {
    if (!follows) return false;
    return follows.some(f => f.entityId === entityId && f.type === type);
  };
  
  // Handle follow action
  const handleFollow = (entity: EntitySearchResult, type: EntityType) => {
    if (isFollowing(entity.id, type)) {
      return; // Already following
    }
    
    followMutation.mutate({
      type,
      entityId: entity.id,
      entityName: entity.name,
      openalexId: entity.openalexId,
    });
  };

  // Save active tab to sessionStorage when it changes
  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY_TAB, activeTab);
  }, [activeTab]);

  // Save scroll position to sessionStorage (per tab)
  const saveScrollPosition = () => {
    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    const storageKey = activeTab === 'following' 
      ? STORAGE_KEY_SCROLL_FOLLOWING 
      : STORAGE_KEY_SCROLL_FORYOU;
    sessionStorage.setItem(storageKey, scrollPosition.toString());
  };

  // Restore scroll position on mount or tab change
  useEffect(() => {
    const storageKey = activeTab === 'following' 
      ? STORAGE_KEY_SCROLL_FOLLOWING 
      : STORAGE_KEY_SCROLL_FORYOU;
    const savedScroll = sessionStorage.getItem(storageKey);
    if (savedScroll) {
      const scrollPosition = parseInt(savedScroll, 10);
      // Use setTimeout to ensure DOM is ready
      setTimeout(() => {
        window.scrollTo({
          top: scrollPosition,
          behavior: 'auto' // Instant scroll, not smooth
        });
      }, 100);
    }
  }, [activeTab]); // Restore when tab changes

  // Listen to scroll events and save position (debounced)
  useEffect(() => {
    const handleScroll = () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      scrollTimeoutRef.current = window.setTimeout(() => {
        const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        const storageKey = activeTab === 'following' 
          ? STORAGE_KEY_SCROLL_FOLLOWING 
          : STORAGE_KEY_SCROLL_FORYOU;
        sessionStorage.setItem(storageKey, scrollPosition.toString());
      }, 150);
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [activeTab]);

  // Get like status for a paper
  const getLikeStatus = (paperId: string): 'liked' | 'disliked' | null => {
    if (feedback.liked.includes(paperId)) return 'liked';
    if (feedback.disliked.includes(paperId)) return 'disliked';
    return null;
  };

  // Check if a paper is in any folder
  const isPaperInFolder = (paperId: string): boolean => {
    if (!foldersList) return false;
    return foldersList.some((folder: any) => 
      folder.papers && folder.papers.some((p: Paper) => p.paperId === paperId)
    );
  };

  // Wrap like/dislike to match PaperCard signature
  const handleLike = (paperId: string) => {
    like({ paperId });
  };

  const handleDislike = (paperId: string) => {
    dislike({ paperId });
  };

  // Handle add to folder
  const handleAddToFolder = (paperId: string) => {
    const paper = papersToShow.find((p: any) => p.paperId === paperId);
    if (paper) {
      setSelectedPaperForFolder(paper);
    }
  };

  // Handle folder selection
  const handleSelectFolder = (folderId: string) => {
    if (!selectedPaperForFolder) return;
    
    // Only like the paper when adding to the "Likes" folder
    if (folderId === 'likes' && !feedback.liked.includes(selectedPaperForFolder.paperId)) {
      like({ paperId: selectedPaperForFolder.paperId, paperData: selectedPaperForFolder });
    }
    
    addPaperMutation.mutate({
      folderId,
      paperId: selectedPaperForFolder.paperId,
      paperData: selectedPaperForFolder,
    });
    
    setSelectedPaperForFolder(null);
  };

  // Handle create new folder
  const handleCreateFolder = async (name: string, description?: string) => {
    await createFolderMutation.mutateAsync({
      name,
      description,
    });
    // Refetch folders after creation to ensure the new folder appears
    await refetchFolders();
  };

  // Get papers to display based on active tab
  const papersToShow = activeTab === 'following' 
    ? (followedPapers || [])
    : (recommendations || []);

  const handleTabChange = (newTab: TabType) => {
    // Save current scroll position before switching tabs
    saveScrollPosition();
    setActiveTab(newTab);
  };

  return (
    <div className="home-page">
      <div className="home-tabs">
        <button
          className={`home-tab ${activeTab === 'following' ? 'active' : ''}`}
          onClick={() => handleTabChange('following')}
        >
          Following
        </button>
        <button
          className={`home-tab ${activeTab === 'foryou' ? 'active' : ''}`}
          onClick={() => handleTabChange('foryou')}
        >
          For You
        </button>
      </div>

      <div className="home-content">
        {activeTab === 'following' && (
          <div className="tab-content">
            <EntitySearch
              onFollow={handleFollow}
              isFollowing={isFollowing}
            />
            
            <FollowedEntitiesList />
            
            {isLoadingFollowedPapers && <LoadingSpinner text="Loading papers from followed entities..." />}
            {isErrorFollowedPapers && (
              <ErrorMessage
                message={followedPapersError?.message || "Failed to load followed papers"}
                onRetry={() => window.location.reload()}
              />
            )}
            {!isLoadingFollowedPapers && !isErrorFollowedPapers && (
              <>
                {papersToShow.length === 0 ? (
                  <div className="empty-state">
                    <p>No papers from followed entities yet.</p>
                    <p className="empty-state-hint">Follow authors, institutions, topics, or journals to see their latest papers here.</p>
                  </div>
                ) : (
                  <div className="papers-container">
                    {papersToShow.map((paper: any) => (
                      <PaperCard
                        key={paper.paperId}
                        paper={paper}
                        likeStatus={getLikeStatus(paper.paperId)}
                        addedToFolder={isPaperInFolder(paper.paperId)}
                        onLike={handleLike}
                        onDislike={handleDislike}
                        onAddToFolder={handleAddToFolder}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'foryou' && (
          <div className="tab-content">
            {isLoadingRecommendations && <LoadingSpinner />}
            {isErrorRecommendations && (
              <ErrorMessage
                message={recommendationsError?.message || "Failed to load recommendations"}
                onRetry={() => window.location.reload()}
              />
            )}
            {!isLoadingRecommendations && !isErrorRecommendations && (
              <>
                {papersToShow.length === 0 ? (
                  <div className="empty-state">
                    <p>No recommendations available yet.</p>
                    <p className="empty-state-hint">Complete your profile to get personalized recommendations.</p>
                  </div>
                ) : (
                  <div className="papers-container">
                    {papersToShow.map((paper) => (
                      <PaperCard
                        key={paper.paperId}
                        paper={paper}
                        likeStatus={getLikeStatus(paper.paperId)}
                        addedToFolder={isPaperInFolder(paper.paperId)}
                        onLike={handleLike}
                        onDislike={handleDislike}
                        onAddToFolder={handleAddToFolder}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {selectedPaperForFolder && (
        <FolderModal
          isOpen={!!selectedPaperForFolder}
          onClose={() => setSelectedPaperForFolder(null)}
          folders={foldersList || []}
          onSelectFolder={handleSelectFolder}
          onCreateFolder={handleCreateFolder}
        />
      )}
    </div>
  );
};

