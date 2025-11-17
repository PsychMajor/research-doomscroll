import apiClient from './client';

export const authApi = {
  // Check authentication status
  checkAuth: async (): Promise<{ authenticated: boolean; user?: any }> => {
    const { data } = await apiClient.get('/api/auth/status');
    return data;
  },

  // Login (redirects to Google OAuth)
  login: () => {
    window.location.href = '/api/auth/login';
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.get('/api/auth/logout');
    window.location.href = '/';
  },
};
