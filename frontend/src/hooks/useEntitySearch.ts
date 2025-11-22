import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { entitySearchApi, type EntityType, type EntitySearchResult } from '../api/entitySearch';

interface UseEntitySearchOptions {
  /**
   * Debounce delay in milliseconds (default: 300ms)
   */
  debounceMs?: number;
  /**
   * Minimum query length to trigger search (default: 2)
   */
  minQueryLength?: number;
  /**
   * Maximum number of results (default: 10)
   */
  limit?: number;
  /**
   * Whether search is enabled (default: true)
   */
  enabled?: boolean;
}

interface UseEntitySearchReturn {
  results: EntitySearchResult[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
}

export const useEntitySearch = (
  query: string,
  entityType: EntityType,
  options?: UseEntitySearchOptions
): UseEntitySearchReturn => {
  const {
    debounceMs = 300,
    minQueryLength = 2,
    limit = 10,
    enabled = true,
  } = options || {};

  const [debouncedQuery, setDebouncedQuery] = useState('');
  const debounceTimerRef = useRef<number | null>(null);

  // Debounce query input
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    const trimmedQuery = query.trim();

    // Reset if query is too short
    if (trimmedQuery.length < minQueryLength) {
      setDebouncedQuery('');
      return;
    }

    // Set up debounce timer
    debounceTimerRef.current = setTimeout(() => {
      setDebouncedQuery(trimmedQuery);
    }, debounceMs);

    // Cleanup on unmount
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, debounceMs, minQueryLength]);

  // React Query for fetching search results
  const shouldFetch = enabled && debouncedQuery.length >= minQueryLength;
  const { data, isLoading, error } = useQuery({
    queryKey: ['entitySearch', entityType, debouncedQuery, limit],
    queryFn: async () => {
      switch (entityType) {
        case 'author':
          return await entitySearchApi.searchAuthors(debouncedQuery, limit);
        case 'institution':
          return await entitySearchApi.searchInstitutions(debouncedQuery, limit);
        case 'topic':
          return await entitySearchApi.searchTopics(debouncedQuery, limit);
        case 'source':
          return await entitySearchApi.searchSources(debouncedQuery, limit);
        default:
          return [];
      }
    },
    enabled: shouldFetch,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
    refetchOnWindowFocus: false,
  });

  return {
    results: data || [],
    isLoading,
    isError: !!error,
    error: error || null,
  };
};

