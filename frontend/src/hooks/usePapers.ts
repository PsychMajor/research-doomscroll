import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { papersApi } from '../api';
import type { SearchParams } from '../types/paper';

export const usePapers = () => {
  const queryClient = useQueryClient();

  // Search papers with pagination
  const useSearchPapers = (params: SearchParams | null) => {
    return useInfiniteQuery({
      queryKey: ['papers', 'search', params],
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
    useSearchPapers,
    usePaper,
    useRecommendations,
    useSimilarPapers,
  };
};
