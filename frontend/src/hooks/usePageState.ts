/**
 * Page State Manager Hook
 * 
 * Generic hook for managing page-specific state that persists across navigation.
 * Each page can save and restore its own state independently.
 */

import { useState, useEffect, useCallback } from 'react';

const STATE_PREFIX = 'page:state:';

/**
 * Save page state to sessionStorage
 */
const savePageState = <T>(route: string, state: T): void => {
  try {
    const key = `${STATE_PREFIX}${route}`;
    sessionStorage.setItem(key, JSON.stringify({ state, timestamp: Date.now() }));
  } catch (error) {
    console.warn(`Failed to save page state for ${route}:`, error);
  }
};

/**
 * Get page state from sessionStorage
 */
const getPageState = <T>(route: string, maxAge: number = 60 * 60 * 1000): T | null => {
  try {
    const key = `${STATE_PREFIX}${route}`;
    const saved = sessionStorage.getItem(key);
    if (saved) {
      const parsed = JSON.parse(saved);
      // Check if state is still valid (not too old)
      if (Date.now() - parsed.timestamp < maxAge) {
        return parsed.state as T;
      } else {
        // Remove expired state
        sessionStorage.removeItem(key);
      }
    }
  } catch (error) {
    console.warn(`Failed to get page state for ${route}:`, error);
  }
  return null;
};

/**
 * Clear page state
 */
const clearPageState = (route: string): void => {
  try {
    const key = `${STATE_PREFIX}${route}`;
    sessionStorage.removeItem(key);
  } catch (error) {
    console.warn(`Failed to clear page state for ${route}:`, error);
  }
};

/**
 * Hook to manage page-specific state with persistence
 */
export const usePageState = <T>(
  route: string,
  initialState: T,
  maxAge: number = 60 * 60 * 1000 // 1 hour default
) => {
  const [state, setState] = useState<T>(() => {
    const cached = getPageState<T>(route, maxAge);
    return cached !== null ? cached : initialState;
  });

  // Save state whenever it changes
  useEffect(() => {
    savePageState(route, state);
  }, [route, state]);

  // Clear state on unmount if needed (optional)
  const clearState = useCallback(() => {
    clearPageState(route);
    setState(initialState);
  }, [route, initialState]);

  return [state, setState, clearState] as const;
};

