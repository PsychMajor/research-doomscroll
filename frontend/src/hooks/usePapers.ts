import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { papersApi } from '../api';
import type { SearchParams } from '../types/paper';

export const usePapers = () => {

  // Search papers with natural language query
  const useSearchPapersByQuery = (query: string | null, sortBy: string = 'recency') => {
    const isEnabled = !!query && typeof query === 'string' && query.trim().length > 0;
    
    return useInfiniteQuery({
      queryKey: ['papers', 'search', 'query', query || '', sortBy],
      queryFn: ({ pageParam = 1 }) => {
        if (!query) {
          throw new Error('Query is required');
        }
        return papersApi.searchByQuery(query, sortBy, pageParam);
      },
      getNextPageParam: (lastPage, allPages) => {
        // If we got 200 papers (full page), there might be more
        if (lastPage.length === 200) {
          return allPages.length + 1;
        }
        return undefined;
      },
      initialPageParam: 1,
      enabled: isEnabled,
      // Keep data in cache even when query is disabled
      gcTime: 24 * 60 * 60 * 1000, // 24 hours
      staleTime: 5 * 60 * 1000, // 5 minutes - consider data fresh for 5 minutes
      retry: 1,
      refetchOnMount: false, // Use cached data if available
      refetchOnWindowFocus: false, // Don't refetch on window focus
    });
  };

  // Search papers with pagination
  const useSearchPapers = (params: SearchParams | null) => {
    // Create a stable query key that doesn't change with object reference
    const queryKey = params
      ? ['papers', 'search', params.topics || '', params.authors || '', params.sortBy || 'recency']
      : ['papers', 'search', null];
    
    return useInfiniteQuery({
      queryKey,
      queryFn: ({ pageParam = 1 }) =>
        papersApi.search({
          ...params!,
          page: pageParam,
        }),
      getNextPageParam: (lastPage, allPages) => {
        // If we got 200 papers (full page), there might be more
        if (lastPage.length === 200) {
          return allPages.length + 1;
        }
        return undefined;
      },
      initialPageParam: 1,
      enabled: !!params && !!(params.topics || params.authors),
      // Keep data in cache even when query is disabled
      gcTime: 24 * 60 * 60 * 1000, // 24 hours
      staleTime: 5 * 60 * 1000, // 5 minutes - consider data fresh for 5 minutes
    });
  };

  // Get paper by ID
  const usePaper = (paperId: string | null) => {
    return useQuery({
      queryKey: ['papers', paperId],
      queryFn: () => papersApi.getById(paperId!),
      enabled: !!paperId,
    });
  };

  // Get recommendations
  const useRecommendations = (limit: number = 20) => {
    return useQuery({
      queryKey: ['papers', 'recommendations', limit],
      queryFn: () => papersApi.getRecommendations(limit),
      staleTime: 10 * 60 * 1000, // 10 minutes
    });
  };

  // Get similar papers
  const useSimilarPapers = (paperId: string | null, limit: number = 10) => {
    return useQuery({
      queryKey: ['papers', paperId, 'similar', limit],
      queryFn: () => papersApi.getSimilar(paperId!, limit),
      enabled: !!paperId,
    });
  };

  return {
    useSearchPapersByQuery,
    useSearchPapers,
    usePaper,
    useRecommendations,
    useSimilarPapers,
  };
};
