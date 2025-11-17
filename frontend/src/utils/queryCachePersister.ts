/**
 * React Query Cache Persister
 * 
 * Persists React Query cache to localStorage so it survives page refreshes.
 * Uses @tanstack/react-query-persist-client for persistence.
 */

import type { PersistQueryClientOptions } from '@tanstack/react-query-persist-client';
import { QueryClient } from '@tanstack/react-query';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

const CACHE_KEY = 'REACT_QUERY_OFFLINE_CACHE';
const MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours

/**
 * Create a localStorage persister for React Query
 */
export const createQueryPersister = () => {
  return createSyncStoragePersister({
    storage: window.localStorage,
    key: CACHE_KEY,
    serialize: JSON.stringify,
    deserialize: JSON.parse,
  });
};

/**
 * Configure React Query client with persistence
 */
export const createPersistedQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 30 * 1000, // 30 seconds
        gcTime: MAX_AGE, // Garbage collect after 24 hours
      },
    },
  });
};

/**
 * Get persist options for PersistQueryClientProvider
 */
export const getPersistOptions = (persister: ReturnType<typeof createQueryPersister>): PersistQueryClientOptions => {
  return {
    persister,
    maxAge: MAX_AGE,
    dehydrateOptions: {
      shouldDehydrateQuery: (query) => {
        // Only persist certain queries to avoid storing too much data
        const queryKey = query.queryKey;
        
        // Persist paper searches and individual papers
        if (Array.isArray(queryKey) && queryKey[0] === 'papers') {
          return true;
        }
        
        // Persist feedback
        if (Array.isArray(queryKey) && queryKey[0] === 'feedback') {
          return true;
        }
        
        // Persist profile
        if (Array.isArray(queryKey) && queryKey[0] === 'profile') {
          return true;
        }
        
        return false;
      },
    },
  };
};

