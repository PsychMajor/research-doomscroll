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

  // Update research interests
  const useUpdateInterests = () => {
    return useMutation({
      mutationFn: (interests: string[]) => profileApi.updateInterests(interests),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Get liked papers
  const useLikedPapers = () => {
    return useQuery({
      queryKey: ['profile', 'liked-papers'],
      queryFn: profileApi.getLikedPapers,
    });
  };

  // Get disliked papers
  const useDislikedPapers = () => {
    return useQuery({
      queryKey: ['profile', 'disliked-papers'],
      queryFn: profileApi.getDislikedPapers,
    });
  };

  return {
    useUserProfile,
    useUpdateInterests,
    useLikedPapers,
    useDislikedPapers,
  };
};
