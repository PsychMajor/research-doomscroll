import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { followsApi, type Follow, type FollowEntityRequest, type FollowEntityType } from '../api/follows';

/**
 * Hook to get all user's follows
 */
export const useFollows = () => {
  return useQuery({
    queryKey: ['follows'],
    queryFn: async () => {
      return await followsApi.getFollows();
    },
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to follow an entity
 */
export const useFollowEntity = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: FollowEntityRequest) => {
      return await followsApi.followEntity(request);
    },
    onSuccess: () => {
      // Invalidate follows list
      queryClient.invalidateQueries({ queryKey: ['follows'] });
      // Invalidate followed papers
      queryClient.invalidateQueries({ queryKey: ['followedPapers'] });
    },
  });
};

/**
 * Hook to unfollow an entity
 */
export const useUnfollowEntity = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ entityType, entityId }: { entityType: FollowEntityType; entityId: string }) => {
      return await followsApi.unfollowEntity(entityType, entityId);
    },
    onSuccess: () => {
      // Invalidate follows list
      queryClient.invalidateQueries({ queryKey: ['follows'] });
      // Invalidate followed papers
      queryClient.invalidateQueries({ queryKey: ['followedPapers'] });
    },
  });
};

/**
 * Hook to get papers from all followed entities
 */
export const useFollowedPapers = (limitPerEntity: number = 50, totalLimit: number = 200) => {
  return useQuery({
    queryKey: ['followedPapers', limitPerEntity, totalLimit],
    queryFn: async () => {
      const response = await followsApi.getFollowedPapers(limitPerEntity, totalLimit);
      return response.papers;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

