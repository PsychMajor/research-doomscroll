import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { feedbackApi } from '../api';
import type { Paper } from '../types/paper';

export const useFeedback = () => {
  const queryClient = useQueryClient();

  // Get feedback data
  const feedbackQuery = useQuery({
    queryKey: ['feedback'],
    queryFn: feedbackApi.getFeedback,
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 1, // Only retry once on failure
  });

  // Like a paper
  const likeMutation = useMutation({
    mutationFn: ({ paperId, paperData }: { paperId: string; paperData?: Paper }) =>
      feedbackApi.like(paperId, paperData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback'] });
    },
  });

  // Unlike a paper
  const unlikeMutation = useMutation({
    mutationFn: (paperId: string) => feedbackApi.unlike(paperId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback'] });
    },
  });

  // Dislike a paper
  const dislikeMutation = useMutation({
    mutationFn: ({ paperId, paperData }: { paperId: string; paperData?: Paper }) =>
      feedbackApi.dislike(paperId, paperData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback'] });
    },
  });

  // Undislike a paper
  const undislikeMutation = useMutation({
    mutationFn: (paperId: string) => feedbackApi.undislike(paperId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback'] });
    },
  });

  return {
    feedback: feedbackQuery.data ?? { liked: [], disliked: [] }, // Provide default empty arrays
    isLoading: feedbackQuery.isLoading,
    isError: feedbackQuery.isError,
    error: feedbackQuery.error,
    like: likeMutation.mutate,
    unlike: unlikeMutation.mutate,
    dislike: dislikeMutation.mutate,
    undislike: undislikeMutation.mutate,
  };
};
