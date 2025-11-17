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
    retryOnMount: false,
    refetchOnMount: false,
    refetchOnWindowFocus: false, // Prevent refetch on window focus to avoid flickering
  });

  // Like a paper with optimistic updates
  const likeMutation = useMutation({
    mutationFn: ({ paperId, paperData }: { paperId: string; paperData?: Paper }) =>
      feedbackApi.like(paperId, paperData),
    onMutate: async ({ paperId }) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ['feedback'] });

      // Snapshot the previous value for rollback
      const previousFeedback = queryClient.getQueryData(['feedback']);

      // Optimistically update the feedback cache
      queryClient.setQueryData(['feedback'], (old: any) => {
        if (!old) return { liked: [paperId], disliked: [] };
        const liked = old.liked || [];
        const disliked = old.disliked || [];
        // Add to liked if not already there, remove from disliked if present
        return {
          liked: liked.includes(paperId) ? liked : [...liked, paperId],
          disliked: disliked.filter((id: string) => id !== paperId),
        };
      });

      // Return context with previous value for rollback
      return { previousFeedback };
    },
    onError: (_err, _variables, context) => {
      // Rollback to previous state on error
      if (context?.previousFeedback) {
        queryClient.setQueryData(['feedback'], context.previousFeedback);
      }
    },
    onSettled: () => {
      // Invalidate other queries but don't refetch feedback immediately to avoid flickering
      // The optimistic update already has the correct state
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  // Unlike a paper with optimistic updates
  const unlikeMutation = useMutation({
    mutationFn: (paperId: string) => feedbackApi.unlike(paperId),
    onMutate: async (paperId) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ['feedback'] });

      // Snapshot the previous value for rollback
      const previousFeedback = queryClient.getQueryData(['feedback']);

      // Optimistically update the feedback cache
      queryClient.setQueryData(['feedback'], (old: any) => {
        if (!old) return { liked: [], disliked: [] };
        return {
          liked: (old.liked || []).filter((id: string) => id !== paperId),
          disliked: old.disliked || [],
        };
      });

      // Return context with previous value for rollback
      return { previousFeedback };
    },
    onError: (_err, _variables, context) => {
      // Rollback to previous state on error
      if (context?.previousFeedback) {
        queryClient.setQueryData(['feedback'], context.previousFeedback);
      }
    },
    onSettled: () => {
      // Invalidate other queries but don't refetch feedback immediately to avoid flickering
      // The optimistic update already has the correct state
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  // Dislike a paper with optimistic updates
  const dislikeMutation = useMutation({
    mutationFn: ({ paperId, paperData }: { paperId: string; paperData?: Paper }) =>
      feedbackApi.dislike(paperId, paperData),
    onMutate: async ({ paperId }) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ['feedback'] });

      // Snapshot the previous value for rollback
      const previousFeedback = queryClient.getQueryData(['feedback']);

      // Optimistically update the feedback cache
      queryClient.setQueryData(['feedback'], (old: any) => {
        if (!old) return { liked: [], disliked: [paperId] };
        const liked = old.liked || [];
        const disliked = old.disliked || [];
        // Add to disliked if not already there, remove from liked if present
        return {
          liked: liked.filter((id: string) => id !== paperId),
          disliked: disliked.includes(paperId) ? disliked : [...disliked, paperId],
        };
      });

      // Return context with previous value for rollback
      return { previousFeedback };
    },
    onError: (_err, _variables, context) => {
      // Rollback to previous state on error
      if (context?.previousFeedback) {
        queryClient.setQueryData(['feedback'], context.previousFeedback);
      }
    },
    onSettled: () => {
      // Invalidate other queries but don't refetch feedback immediately to avoid flickering
      // The optimistic update already has the correct state
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  // Undislike a paper with optimistic updates
  const undislikeMutation = useMutation({
    mutationFn: (paperId: string) => feedbackApi.undislike(paperId),
    onMutate: async (paperId) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ['feedback'] });

      // Snapshot the previous value for rollback
      const previousFeedback = queryClient.getQueryData(['feedback']);

      // Optimistically update the feedback cache
      queryClient.setQueryData(['feedback'], (old: any) => {
        if (!old) return { liked: [], disliked: [] };
        return {
          liked: old.liked || [],
          disliked: (old.disliked || []).filter((id: string) => id !== paperId),
        };
      });

      // Return context with previous value for rollback
      return { previousFeedback };
    },
    onError: (_err, _variables, context) => {
      // Rollback to previous state on error
      if (context?.previousFeedback) {
        queryClient.setQueryData(['feedback'], context.previousFeedback);
      }
    },
    onSettled: () => {
      // Invalidate other queries but don't refetch feedback immediately to avoid flickering
      // The optimistic update already has the correct state
      queryClient.invalidateQueries({ queryKey: ['folders'] });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
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
