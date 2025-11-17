/**
 * Scroll Position Manager
 * 
 * Manages scroll position persistence across page navigation.
 * Similar to Twitter's behavior where scroll position is restored when navigating back.
 */

const SCROLL_PREFIX = 'scroll:';

/**
 * Save scroll position for a specific route
 */
export const saveScrollPosition = (route: string, position: number): void => {
  try {
    const key = `${SCROLL_PREFIX}${route}`;
    sessionStorage.setItem(key, position.toString());
  } catch (error) {
    console.warn('Failed to save scroll position:', error);
  }
};

/**
 * Get saved scroll position for a specific route
 */
export const getScrollPosition = (route: string): number | null => {
  try {
    const key = `${SCROLL_PREFIX}${route}`;
    const saved = sessionStorage.getItem(key);
    return saved ? parseInt(saved, 10) : null;
  } catch (error) {
    console.warn('Failed to get scroll position:', error);
    return null;
  }
};

/**
 * Clear scroll position for a specific route
 */
export const clearScrollPosition = (route: string): void => {
  try {
    const key = `${SCROLL_PREFIX}${route}`;
    sessionStorage.removeItem(key);
  } catch (error) {
    console.warn('Failed to clear scroll position:', error);
  }
};

/**
 * Restore scroll position for a specific route
 * Returns true if scroll was restored, false otherwise
 */
export const restoreScrollPosition = (route: string, container?: HTMLElement | null): boolean => {
  const position = getScrollPosition(route);
  if (position === null) return false;

  try {
    // Use requestAnimationFrame to ensure DOM is ready
    requestAnimationFrame(() => {
      if (container) {
        container.scrollTop = position;
      } else {
        window.scrollTo(0, position);
      }
    });
    return true;
  } catch (error) {
    console.warn('Failed to restore scroll position:', error);
    return false;
  }
};

/**
 * Setup scroll listener to save position on scroll
 */
export const setupScrollListener = (
  route: string,
  container?: HTMLElement | null,
  throttleMs: number = 200
): (() => void) => {
  let timeoutId: NodeJS.Timeout | null = null;

  const handleScroll = () => {
    if (timeoutId) return;

    timeoutId = setTimeout(() => {
      const scrollPosition = container
        ? container.scrollTop
        : window.scrollY || document.documentElement.scrollTop;

      saveScrollPosition(route, scrollPosition);
      timeoutId = null;
    }, throttleMs);
  };

  const target = container || window;
  target.addEventListener('scroll', handleScroll, { passive: true });

  // Return cleanup function
  return () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    target.removeEventListener('scroll', handleScroll);
  };
};

