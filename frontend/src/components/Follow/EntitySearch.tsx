import React, { useState, useRef, useEffect } from 'react';
import { entitySearchApi } from '../../api/entitySearch';
import type { EntityType, EntitySearchResult } from '../../api/entitySearch';
import './EntitySearch.css';

interface EntitySearchProps {
  onFollow: (entity: EntitySearchResult, type: EntityType) => void;
  isFollowing: (entityId: string, type: EntityType) => boolean;
}

export const EntitySearch: React.FC<EntitySearchProps> = ({ onFollow, isFollowing }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<Array<EntitySearchResult & { type: EntityType }>>([]);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Search all entity types simultaneously
  useEffect(() => {
    const searchAllTypes = async () => {
      if (searchQuery.trim().length < 2) {
        setResults([]);
        setShowResults(false);
        return;
      }

      setIsLoading(true);
      try {
        const [authors, institutions, topics, sources] = await Promise.all([
          entitySearchApi.searchAuthors(searchQuery, 5),
          entitySearchApi.searchInstitutions(searchQuery, 5),
          entitySearchApi.searchTopics(searchQuery, 5),
          entitySearchApi.searchSources(searchQuery, 5),
        ]);

        // Combine all results with their types
        const allResults: Array<EntitySearchResult & { type: EntityType }> = [
          ...authors.map(r => ({ ...r, type: 'author' as EntityType })),
          ...institutions.map(r => ({ ...r, type: 'institution' as EntityType })),
          ...topics.map(r => ({ ...r, type: 'topic' as EntityType })),
          ...sources.map(r => ({ ...r, type: 'source' as EntityType })),
        ];

        setResults(allResults);
        if (allResults.length > 0) {
          setShowResults(true);
        }
      } catch (error) {
        console.error('Error searching entities:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    const debounceTimer = setTimeout(searchAllTypes, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery]);


  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleFollow = async (entity: EntitySearchResult & { type: EntityType }, event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    // If this is a query-based entity, follow it as a custom query
    if (entity.id.startsWith('query-')) {
      const query = entity.name.trim();
      console.log(`🔍 Following custom query: "${query}"`);
      
      // Create a custom entity to follow
      // Use a hash of the query as the entityId for uniqueness
      const queryHash = btoa(query).replace(/[+/=]/g, '').substring(0, 20);
      const customEntity: EntitySearchResult = {
        id: queryHash,
        openalexId: query,
        name: query,
        worksCount: 0,
      };
      
      // Follow as custom type - backend will parse it with GPT
      onFollow(customEntity, 'custom' as EntityType);
    } else {
      // Regular entity, follow directly with its type
      console.log(`✅ Following entity:`, entity);
      onFollow(entity, entity.type);
    }
    
    setShowResults(false);
    setSearchQuery('');
  };

  const handleInputFocus = () => {
    if (results.length > 0 && searchQuery.length >= 2) {
      setShowResults(true);
    }
  };

  const typeLabels: Record<EntityType, string> = {
    author: 'Author',
    institution: 'Institution',
    topic: 'Topic',
    source: 'Journal',
  };

  return (
    <div className="entity-search">
      <div className="entity-search-input-wrapper" ref={wrapperRef}>
        <div className="entity-search-input-container">
          <svg className="entity-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            className="entity-search-input"
            placeholder="Search for authors, institutions, topics, or journals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={handleInputFocus}
          />
        </div>
        {isLoading && <div className="entity-search-loading">Searching...</div>}
        {showResults && (results.length > 0 || searchQuery.trim().length >= 2) && (
          <div className="entity-search-results">
          {(() => {
            const displayResults = [...results];
            
            // Always add the exact query as the first result, even if there's a match
            if (searchQuery.trim().length >= 2) {
              const queryEntity: EntitySearchResult & { type: EntityType } = {
                id: `query-${searchQuery.trim()}`,
                openalexId: `query-${searchQuery.trim()}`,
                name: searchQuery.trim(),
                worksCount: 0,
                type: 'topic' as EntityType, // Default type for query
              };
              displayResults.unshift(queryEntity);
            }
            
            return displayResults.map((entity) => {
              const following = isFollowing(entity.id, entity.type);
              const isQueryResult = entity.id.startsWith('query-');
              return (
                <div key={`${entity.type}-${entity.id}`} className="entity-result-item">
                  <div className="entity-info">
                    <div className="entity-name">
                      {entity.name}
                      {!isQueryResult && <span className="entity-type-badge">{typeLabels[entity.type]}</span>}
                    </div>
                    <div className="entity-meta">
                      {!isQueryResult && entity.worksCount > 0 && (
                        <span className="entity-works-count">{entity.worksCount.toLocaleString()} papers</span>
                      )}
                    </div>
                  </div>
                  <button
                    className={`follow-btn ${following ? 'following' : ''}`}
                    onClick={(e) => handleFollow(entity, e)}
                    disabled={following}
                  >
                    {following ? 'Following' : 'Follow'}
                  </button>
                </div>
              );
            });
          })()}
          </div>
        )}
      </div>

      {searchQuery.length >= 2 && results.length === 0 && !isLoading && (
        <div className="entity-search-empty">
          No results found for "{searchQuery}"
        </div>
      )}
    </div>
  );
};

