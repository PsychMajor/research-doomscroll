import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { papersApi } from '../api';
import type { SearchParams } from '../types/paper';

export const usePapers = () => {
  const queryClient = useQueryClient();

  // Search papers with infinite scroll
  const useSearchPapers = (params: SearchParams) => {
    return useInfiniteQuery({
      queryKey: ['papers', 'search', params],
      queryFn: ({ pageParam = 0 }) =>
        papersApi.search({
          ...params,
          offset: pageParam,
        }),
      getNextPageParam: (lastPage, allPages) => {
        if (!lastPage.has_more) return undefined;
        return allPages.reduce((total, page) => total + page.papers.length, 0);
      },
      initialPageParam: 0,
      enabled: !!(params.query || params.concepts?.length),
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
