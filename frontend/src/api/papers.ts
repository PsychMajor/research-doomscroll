import apiClient from './client';
import type { SearchParams, Paper } from '../types/paper';

export const papersApi = {
  // Search papers with natural language query
  searchByQuery: async (query: string, sortBy: string = 'recency', page: number = 1): Promise<Paper[]> => {
    try {
      const { data } = await apiClient.get('/api/papers/search/query', { 
        params: {
          q: query,
          page: page,
          per_page: 200,
          sort_by: sortBy,
        }
      });
      
      if (data && data.length > 0) {
        console.log(`✅ Search successful: Found ${data.length} papers for "${query}"`);
      } else {
        console.log(`⚠️ Search returned 0 papers for "${query}"`);
      }
      return data || [];
    } catch (error: any) {
      console.error('❌ Error searching papers:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        query
      });
      throw error;
    }
  },

  // Search papers
  search: async (params: SearchParams): Promise<Paper[]> => {
    try {
      console.log('Searching papers with params:', params);
      
      const { data } = await apiClient.get('/api/papers/search', { 
        params: {
          topics: params.topics || '',
          authors: params.authors || '',
          page: params.page || 1,
          per_page: 200,
          sort_by: params.sortBy || 'recency',
        }
      });
      
      console.log('Search successful, received papers:', data?.length || 0);
      return data || [];
    } catch (error: any) {
      console.error('Error searching papers:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        params
      });
      throw error;
    }
  },

  // Get paper by ID
  getById: async (paperId: string): Promise<Paper> => {
    try {
      console.log('Fetching paper:', paperId);
      const { data } = await apiClient.get(`/api/papers/${paperId}`);
      console.log('Paper fetched successfully');
      return data;
    } catch (error: any) {
      console.error('Error fetching paper:', {
        paperId,
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw error;
    }
  },

  // Get recommended papers
  getRecommendations: async (limit: number = 20): Promise<Paper[]> => {
    try {
      console.log('Fetching recommendations, limit:', limit);
      const { data } = await apiClient.get('/api/papers/recommendations', {
        params: { limit },
      });
      console.log('Recommendations fetched:', data?.length || 0);
      return data || [];
    } catch (error: any) {
      console.error('Error fetching recommendations:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw error;
    }
  },

  // Get similar papers
  getSimilar: async (paperId: string, limit: number = 10): Promise<Paper[]> => {
    try {
      console.log('Fetching similar papers for:', paperId);
      const { data } = await apiClient.get(`/api/papers/${paperId}/similar`, {
        params: { limit },
      });
      console.log('Similar papers fetched:', data?.length || 0);
      return data || [];
    } catch (error: any) {
      console.error('Error fetching similar papers:', {
        paperId,
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw error;
    }
  },
};
