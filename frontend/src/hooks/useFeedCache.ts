/**
 * Feed Cache Hook
 * 
 * Manages caching of feed state including form inputs, search params, and active search.
 * Preserves user's work when navigating away from the feed page.
 */

import { useState, useEffect, useCallback } from 'react';
import type { SearchParams } from '../types/paper';

const CACHE_KEY = 'feed:state';
const FORM_CACHE_KEY = 'feed:form';

interface FeedCacheState {
  topics: string;
  authors: string;
  sortBy: 'recency' | 'relevance';
  activeSearch: SearchParams | null;
  unifiedSearchQuery?: string; // Unified search query
  useUnifiedSearch?: boolean; // Whether unified search is active
  timestamp: number;
}

interface FeedFormState {
  topics: string;
  authors: string;
  sortBy: 'recency' | 'relevance';
}

/**
 * Save feed state to sessionStorage
 */
const saveFeedState = (state: Partial<FeedCacheState>): void => {
  try {
    const existing = getFeedState();
    const newState: FeedCacheState = {
      ...existing,
      ...state,
      timestamp: Date.now(),
    };
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(newState));
  } catch (error) {
    console.warn('Failed to save feed state:', error);
  }
};

/**
 * Get feed state from sessionStorage
 */
export const getFeedState = (): FeedCacheState => {
  try {
    const saved = sessionStorage.getItem(CACHE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.warn('Failed to get feed state:', error);
  }
  return {
    topics: '',
    authors: '',
    sortBy: 'recency',
    activeSearch: null,
    timestamp: 0,
  };
};

/**
 * Save form state separately (for form inputs)
 */
const saveFormState = (formState: FeedFormState): void => {
  try {
    sessionStorage.setItem(FORM_CACHE_KEY, JSON.stringify(formState));
  } catch (error) {
    console.warn('Failed to save form state:', error);
  }
};

/**
 * Get form state from sessionStorage
 */
export const getFormState = (): FeedFormState | null => {
  try {
    const saved = sessionStorage.getItem(FORM_CACHE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.warn('Failed to get form state:', error);
  }
  return null;
};

/**
 * Clear feed cache
 */
export const clearFeedCache = (): void => {
  try {
    sessionStorage.removeItem(CACHE_KEY);
    sessionStorage.removeItem(FORM_CACHE_KEY);
  } catch (error) {
    console.warn('Failed to clear feed cache:', error);
  }
};

/**
 * Hook to manage feed cache
 */
export const useFeedCache = () => {
  // Load cached state synchronously on mount (before first render)
  const initialState = (() => {
    const state = getFeedState();
    const maxAge = 60 * 60 * 1000; // 1 hour
    if (state.timestamp && Date.now() - state.timestamp < maxAge) {
      return state;
    }
    return null;
  })();
  
  const initialForm = getFormState();
  
  const [cachedState, setCachedState] = useState<FeedCacheState | null>(initialState);
  const [cachedForm, setCachedForm] = useState<FeedFormState | null>(initialForm);

  // Also load on mount to ensure we have the latest
  useEffect(() => {
    const state = getFeedState();
    const form = getFormState();
    
    // Only use cache if it's less than 1 hour old
    const maxAge = 60 * 60 * 1000; // 1 hour
    if (state.timestamp && Date.now() - state.timestamp < maxAge) {
      setCachedState(state);
    }
    
    if (form) {
      setCachedForm(form);
    }
  }, []);

  const saveState = useCallback((state: Partial<FeedCacheState>) => {
    saveFeedState(state);
    setCachedState((prev) => ({ ...prev, ...state, timestamp: Date.now() } as FeedCacheState));
  }, []);

  const saveForm = useCallback((formState: FeedFormState) => {
    saveFormState(formState);
    setCachedForm(formState);
  }, []);

  const clearCache = useCallback(() => {
    clearFeedCache();
    setCachedState(null);
    setCachedForm(null);
  }, []);

  return {
    cachedState,
    cachedForm,
    saveState,
    saveForm,
    clearCache,
  };
};

