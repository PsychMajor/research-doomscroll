import apiClient from './client';
import type { UserProfileResponse } from '../types/user';

export const profileApi = {
  // Get user profile
  getProfile: async (): Promise<UserProfileResponse> => {
    const { data } = await apiClient.get('/api/profile');
    return data;
  },

  // Update research interests (topics and authors)
  updateProfile: async (topics: string[] = [], authors: string[] = []): Promise<{ status: string }> => {
    const { data } = await apiClient.put('/api/profile', {
      topics,
      authors,
    });
    return data;
  },

  // Clear profile
  clearProfile: async (): Promise<{ status: string }> => {
    const { data } = await apiClient.delete('/api/profile');
    return data;
  },
};
