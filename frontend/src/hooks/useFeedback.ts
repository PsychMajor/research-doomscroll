import { useMutation, useQueryClient } from '@tanstack/react-query';
import { feedbackApi } from '../api';
import type { Feedback } from '../types/feedback';

export const useFeedback = () => {
  const queryClient = useQueryClient();

  // Submit feedback (like/dislike)
  const useSubmitFeedback = () => {
    return useMutation({
      mutationFn: (feedback: Feedback) => feedbackApi.submit(feedback),
      onSuccess: () => {
        // Invalidate profile to refresh liked/disliked papers
        queryClient.invalidateQueries({ queryKey: ['profile'] });
        queryClient.invalidateQueries({ queryKey: ['profile', 'liked-papers'] });
        queryClient.invalidateQueries({ queryKey: ['profile', 'disliked-papers'] });
      },
    });
  };

  // Remove feedback
  const useRemoveFeedback = () => {
    return useMutation({
      mutationFn: (paperId: string) => feedbackApi.remove(paperId),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['profile'] });
        queryClient.invalidateQueries({ queryKey: ['profile', 'liked-papers'] });
        queryClient.invalidateQueries({ queryKey: ['profile', 'disliked-papers'] });
      },
    });
  };

  return {
    useSubmitFeedback,
    useRemoveFeedback,
  };
};
