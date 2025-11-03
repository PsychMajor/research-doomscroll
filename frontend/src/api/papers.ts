import apiClient from './client';
import type { SearchParams, SearchResponse, Paper } from '../types/paper';

export const papersApi = {
  // Search papers
  search: async (params: SearchParams): Promise<SearchResponse> => {
    const { data } = await apiClient.get('/papers/search', { params });
    return data;
  },

  // Get paper by ID
  getById: async (paperId: string): Promise<Paper> => {
    const { data } = await apiClient.get(`/papers/${paperId}`);
    return data;
  },

  // Get recommended papers
  getRecommendations: async (limit: number = 20): Promise<Paper[]> => {
    const { data } = await apiClient.get('/papers/recommendations', {
      params: { limit },
    });
    return data;
  },

  // Get similar papers
  getSimilar: async (paperId: string, limit: number = 10): Promise<Paper[]> => {
    const { data } = await apiClient.get(`/papers/${paperId}/similar`, {
      params: { limit },
    });
    return data;
  },
};
