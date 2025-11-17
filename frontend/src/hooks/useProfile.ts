import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { profileApi } from '../api';

export const useProfile = () => {
  const queryClient = useQueryClient();

  // Get user profile
  const useUserProfile = () => {
    return useQuery({
      queryKey: ['profile'],
      queryFn: profileApi.getProfile,
      staleTime: 5 * 60 * 1000, // 5 minutes
    });
  };

  // Update profile (topics and authors)
  const useUpdateProfile = () => {
    return useMutation({
      mutationFn: ({ topics, authors }: { topics?: string[]; authors?: string[] }) => 
        profileApi.updateProfile(topics || [], authors || []),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Clear profile
  const useClearProfile = () => {
    return useMutation({
      mutationFn: () => profileApi.clearProfile(),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  return {
    useUserProfile,
    useUpdateProfile,
    useClearProfile,
  };
};
