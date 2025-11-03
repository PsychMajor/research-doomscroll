import apiClient from './client';
import type { Feedback, FeedbackResponse } from '../types/feedback';

export const feedbackApi = {
  // Submit feedback (like/dislike)
  submit: async (feedback: Feedback): Promise<FeedbackResponse> => {
    const { data } = await apiClient.post('/feedback', feedback);
    return data;
  },

  // Remove feedback
  remove: async (paperId: string): Promise<{ status: string }> => {
    const { data } = await apiClient.delete(`/feedback/${paperId}`);
    return data;
  },
};
