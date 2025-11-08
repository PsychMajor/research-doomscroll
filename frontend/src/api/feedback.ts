import apiClient from './client';
import type { Paper } from '../types/paper';

export const feedbackApi = {
  // Like a paper
  like: async (paperId: string, paperData?: Paper): Promise<{ status: string }> => {
    const formData = new FormData();
    formData.append('paper_id', paperId);
    if (paperData) {
      formData.append('paper_data', JSON.stringify(paperData));
    }
    
    const { data } = await apiClient.post('/paper/like', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Unlike a paper
  unlike: async (paperId: string): Promise<{ status: string }> => {
    const formData = new FormData();
    formData.append('paper_id', paperId);
    
    const { data } = await apiClient.post('/paper/unlike', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Dislike a paper
  dislike: async (paperId: string, paperData?: Paper): Promise<{ status: string }> => {
    const formData = new FormData();
    formData.append('paper_id', paperId);
    if (paperData) {
      formData.append('paper_data', JSON.stringify(paperData));
    }
    
    const { data } = await apiClient.post('/paper/dislike', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Undislike a paper
  undislike: async (paperId: string): Promise<{ status: string }> => {
    const formData = new FormData();
    formData.append('paper_id', paperId);
    
    const { data } = await apiClient.post('/paper/undislike', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Get feedback data (liked/disliked papers)
  getFeedback: async (): Promise<{ liked: string[]; disliked: string[] }> => {
    const { data } = await apiClient.get('/feedback');
    return data;
  },
};
