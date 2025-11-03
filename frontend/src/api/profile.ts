import apiClient from './client';
import type { UserProfileResponse } from '../types/user';

export const profileApi = {
  // Get user profile
  getProfile: async (): Promise<UserProfileResponse> => {
    const { data } = await apiClient.get('/profile');
    return data;
  },

  // Update research interests
  updateInterests: async (interests: string[]): Promise<{ status: string }> => {
    const { data } = await apiClient.post('/profile/interests', { interests });
    return data;
  },

  // Get liked papers
  getLikedPapers: async (): Promise<string[]> => {
    const { data } = await apiClient.get('/profile/liked-papers');
    return data;
  },

  // Get disliked papers
  getDislikedPapers: async (): Promise<string[]> => {
    const { data } = await apiClient.get('/profile/disliked-papers');
    return data;
  },
};
