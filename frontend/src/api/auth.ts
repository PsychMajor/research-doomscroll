import apiClient from './client';

export const authApi = {
  // Check authentication status
  checkAuth: async (): Promise<{ authenticated: boolean }> => {
    const { data } = await apiClient.get('/auth/status');
    return data;
  },

  // Login (redirects to Google OAuth)
  login: () => {
    window.location.href = '/login';
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.post('/logout');
    window.location.href = '/';
  },
};
