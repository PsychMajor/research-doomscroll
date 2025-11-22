import apiClient from './client';

export type FollowEntityType = 'author' | 'institution' | 'topic' | 'source' | 'custom';

export interface Follow {
  id: string;
  userId: string;
  type: FollowEntityType;
  entityId: string;
  entityName: string;
  openalexId: string;
  followedAt: string;
  updatedAt: string;
}

export interface FollowEntityRequest {
  type: FollowEntityType;
  entityId: string;
  entityName: string;
  openalexId: string;
}

export interface FollowsResponse {
  follows: Follow[];
}

export interface FollowedPapersResponse {
  papers: any[];
  count: number;
}

export const followsApi = {
  /**
   * Follow an entity
   */
  followEntity: async (request: FollowEntityRequest): Promise<{ success: boolean; follow: any }> => {
    const { data } = await apiClient.post('/api/follows', request);
    return data;
  },

  /**
   * Unfollow an entity
   */
  unfollowEntity: async (entityType: FollowEntityType, entityId: string): Promise<{ success: boolean }> => {
    const { data } = await apiClient.delete(`/api/follows/${entityType}/${entityId}`);
    return data;
  },

  /**
   * Get all user's follows
   */
  getFollows: async (): Promise<Follow[]> => {
    const { data } = await apiClient.get<FollowsResponse>('/api/follows');
    return data?.follows || [];
  },

  /**
   * Get papers from all followed entities
   */
  getFollowedPapers: async (
    limitPerEntity: number = 50,
    totalLimit: number = 200
  ): Promise<FollowedPapersResponse> => {
    const { data } = await apiClient.get<FollowedPapersResponse>('/api/follows/papers', {
      params: { limit_per_entity: limitPerEntity, total_limit: totalLimit },
    });
    return data;
  },
};

