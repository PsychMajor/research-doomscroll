import { useState, useEffect, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { autocompleteApi, type AutocompleteSuggestion } from '../api/autocomplete';

interface UseAutocompleteOptions {
  /**
   * Debounce delay in milliseconds (default: 300ms)
   */
  debounceMs?: number;
  /**
   * Minimum query length to trigger autocomplete (default: 2)
   */
  minQueryLength?: number;
  /**
   * Maximum number of suggestions to return (default: 10)
   */
  limit?: number;
  /**
   * Optional comma-separated list of types to search
   */
  types?: string;
  /**
   * Whether autocomplete is enabled (default: true)
   */
  enabled?: boolean;
}

interface UseAutocompleteReturn {
  /**
   * Autocomplete suggestions
   */
  suggestions: AutocompleteSuggestion[];
  /**
   * Whether suggestions are currently loading
   */
  isLoading: boolean;
  /**
   * Error state
   */
  error: Error | null;
  /**
   * Whether to show the dropdown
   */
  showDropdown: boolean;
  /**
   * Currently highlighted suggestion index
   */
  highlightedIndex: number;
  /**
   * Set highlighted index
   */
  setHighlightedIndex: (index: number) => void;
  /**
   * Select a suggestion
   */
  selectSuggestion: (suggestion: AutocompleteSuggestion) => void;
  /**
   * Reset autocomplete state
   */
  reset: () => void;
}

/**
 * Hook for managing autocomplete functionality with debouncing and React Query
 */
export const useAutocomplete = (
  query: string,
  onSelect?: (suggestion: AutocompleteSuggestion) => void,
  options: UseAutocompleteOptions = {}
): UseAutocompleteReturn => {
  const {
    debounceMs = 300,
    minQueryLength = 2,
    limit = 10,
    types,
    enabled = true,
  } = options;

  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Debounce query updates
  useEffect(() => {
    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Cancel any in-flight requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const trimmedQuery = query.trim();

    // Reset if query is too short
    if (trimmedQuery.length < minQueryLength) {
      setDebouncedQuery('');
      setShowDropdown(false);
      setHighlightedIndex(-1);
      console.log('🔍 Query too short, resetting autocomplete:', { trimmedQuery, minQueryLength });
      return;
    }

    console.log('🔍 Setting up debounce timer:', {
      trimmedQuery,
      enabled,
      debounceMs,
    });

    // Set up debounce timer
    debounceTimerRef.current = setTimeout(() => {
      console.log('🔍 Debounce timer fired, setting debounced query:', trimmedQuery);
      setDebouncedQuery(trimmedQuery);
    }, debounceMs);

    // Cleanup on unmount
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [query, debounceMs, minQueryLength]);

  // React Query for fetching suggestions
  const shouldFetch = enabled && debouncedQuery.length >= minQueryLength;
  const { data, isLoading, error } = useQuery({
    queryKey: ['autocomplete', debouncedQuery, limit, types],
    queryFn: async () => {
      // Create new abort controller for this request
      abortControllerRef.current = new AbortController();
      console.log('🔍 Fetching autocomplete suggestions (React Query):', {
        debouncedQuery,
        enabled,
        shouldFetch,
        limit,
        types,
      });
      const suggestions = await autocompleteApi.getSuggestions(debouncedQuery, limit, types);
      console.log('🔍 Autocomplete API response received:', {
        query: debouncedQuery,
        suggestionsCount: suggestions.length,
        suggestions: suggestions.slice(0, 3), // Log first 3
      });
      return suggestions;
    },
    enabled: shouldFetch,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
    refetchOnWindowFocus: false,
  });

  // Update dropdown visibility based on suggestions
  useEffect(() => {
    if (shouldFetch && data && data.length > 0) {
      setShowDropdown(true);
      setHighlightedIndex(-1); // Reset highlight when new suggestions arrive
      console.log('🔍 Showing autocomplete dropdown:', {
        query: debouncedQuery,
        suggestionsCount: data.length,
      });
    } else if (!shouldFetch || !data || data.length === 0) {
      setShowDropdown(false);
      setHighlightedIndex(-1);
    }
  }, [data, shouldFetch, debouncedQuery]);

  // Select suggestion handler
  const selectSuggestion = useCallback(
    (suggestion: AutocompleteSuggestion) => {
      setShowDropdown(false);
      setHighlightedIndex(-1);
      if (onSelect) {
        onSelect(suggestion);
      }
    },
    [onSelect]
  );

  // Reset handler
  const reset = useCallback(() => {
    setShowDropdown(false);
    setHighlightedIndex(-1);
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  return {
    suggestions: data || [],
    isLoading,
    error: error as Error | null,
    showDropdown,
    highlightedIndex,
    setHighlightedIndex,
    selectSuggestion,
    reset,
  };
};

