import apiClient from './client';

export type EntityType = 'author' | 'institution' | 'topic' | 'source';

export interface EntitySearchResult {
  id: string;
  openalexId: string;
  name: string;
  worksCount: number;
  orcid?: string;
  countryCode?: string;
  level?: number;
  issn?: string[];
}

export interface EntitySearchResponse {
  results: EntitySearchResult[];
}

export const entitySearchApi = {
  /**
   * Search for authors
   */
  searchAuthors: async (query: string, limit: number = 10): Promise<EntitySearchResult[]> => {
    try {
      const { data } = await apiClient.get<EntitySearchResponse>('/api/entity-search/authors', {
        params: { q: query, limit },
      });
      return data?.results || [];
    } catch (error: any) {
      console.error('Error searching authors:', error);
      return [];
    }
  },

  /**
   * Search for institutions
   */
  searchInstitutions: async (query: string, limit: number = 10): Promise<EntitySearchResult[]> => {
    try {
      const { data } = await apiClient.get<EntitySearchResponse>('/api/entity-search/institutions', {
        params: { q: query, limit },
      });
      return data?.results || [];
    } catch (error: any) {
      console.error('Error searching institutions:', error);
      return [];
    }
  },

  /**
   * Search for topics/concepts
   */
  searchTopics: async (query: string, limit: number = 10): Promise<EntitySearchResult[]> => {
    try {
      const { data } = await apiClient.get<EntitySearchResponse>('/api/entity-search/topics', {
        params: { q: query, limit },
      });
      return data?.results || [];
    } catch (error: any) {
      console.error('Error searching topics:', error);
      return [];
    }
  },

  /**
   * Search for sources/journals
   */
  searchSources: async (query: string, limit: number = 10): Promise<EntitySearchResult[]> => {
    try {
      const { data } = await apiClient.get<EntitySearchResponse>('/api/entity-search/sources', {
        params: { q: query, limit },
      });
      return data?.results || [];
    } catch (error: any) {
      console.error('Error searching sources:', error);
      return [];
    }
  },
};

