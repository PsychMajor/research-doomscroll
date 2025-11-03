import { useQuery } from '@tanstack/react-query';
import { authApi } from '../api';

export const useAuth = () => {
  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['auth', 'status'],
    queryFn: authApi.checkAuth,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const isAuthenticated = authStatus?.authenticated ?? false;

  const login = () => {
    authApi.login();
  };

  const logout = async () => {
    await authApi.logout();
  };

  return {
    isAuthenticated,
    isLoading,
    login,
    logout,
  };
};
