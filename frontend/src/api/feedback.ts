import apiClient from './client';
import type { Paper } from '../types/paper';

export const feedbackApi = {
  // Like a paper
  like: async (paperId: string, paperData?: Paper): Promise<{ status: string }> => {
    try {
      console.log('Liking paper:', paperId);
      const { data } = await apiClient.post('/api/feedback/like', {
        paper_id: paperId,
        paper_data: paperData,
      });
      console.log('Paper liked successfully');
      return data;
    } catch (error: any) {
      console.error('Error liking paper:', {
        paperId,
        message: error.message,
        response: error.response?.data,
      });
      throw error;
    }
  },

  // Unlike a paper
  unlike: async (paperId: string): Promise<{ status: string }> => {
    try {
      console.log('Unliking paper:', paperId);
      const { data } = await apiClient.delete(`/api/feedback/like/${paperId}`);
      console.log('Paper unliked successfully');
      return data;
    } catch (error: any) {
      console.error('Error unliking paper:', {
        paperId,
        message: error.message,
        response: error.response?.data,
      });
      throw error;
    }
  },

  // Dislike a paper
  dislike: async (paperId: string, paperData?: Paper): Promise<{ status: string }> => {
    try {
      console.log('Disliking paper:', paperId);
      const { data } = await apiClient.post('/api/feedback/dislike', {
        paper_id: paperId,
        paper_data: paperData,
      });
      console.log('Paper disliked successfully');
      return data;
    } catch (error: any) {
      console.error('Error disliking paper:', {
        paperId,
        message: error.message,
        response: error.response?.data,
      });
      throw error;
    }
  },

  // Undislike a paper
  undislike: async (paperId: string): Promise<{ status: string }> => {
    try {
      console.log('Undisliking paper:', paperId);
      const { data } = await apiClient.delete(`/api/feedback/dislike/${paperId}`);
      console.log('Dislike removed successfully');
      return data;
    } catch (error: any) {
      console.error('Error removing dislike:', {
        paperId,
        message: error.message,
        response: error.response?.data,
      });
      throw error;
    }
  },

  // Get feedback data (liked/disliked papers)
  getFeedback: async (): Promise<{ liked: string[]; disliked: string[] }> => {
    try {
      console.log('Fetching feedback data...');
      const { data } = await apiClient.get('/api/feedback');
      console.log('Feedback loaded:', {
        liked: data.liked?.length || 0,
        disliked: data.disliked?.length || 0,
      });
      return data;
    } catch (error: any) {
      console.error('Error fetching feedback:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      // Return empty arrays instead of throwing to prevent UI crash
      if (error.response?.status === 401) {
        console.warn('User not authenticated, returning empty feedback');
        return { liked: [], disliked: [] };
      }
      throw error;
    }
  },
};
