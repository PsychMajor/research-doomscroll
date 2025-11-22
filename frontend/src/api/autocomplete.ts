import apiClient from './client';

export interface AutocompleteSuggestion {
  text: string;
  type: 'paper' | 'author' | 'journal' | 'institution' | 'topic';
  count?: number;
}

export interface AutocompleteResponse {
  suggestions: AutocompleteSuggestion[];
}

export const autocompleteApi = {
  /**
   * Get autocomplete suggestions from OpenAlex API
   * 
   * @param query Search query string (minimum 2 characters)
   * @param limit Maximum number of suggestions (default: 10, max: 20)
   * @param types Optional comma-separated list of types to search
   * @returns Promise with autocomplete suggestions
   */
  getSuggestions: async (
    query: string,
    limit: number = 10,
    types?: string
  ): Promise<AutocompleteSuggestion[]> => {
    if (!query || query.trim().length < 2) {
      return [];
    }

    try {
      const params: any = {
        q: query.trim(),
        limit: Math.min(limit, 20), // Cap at 20
      };

      if (types) {
        params.types = types;
      }

      console.log('🔍 Fetching autocomplete suggestions:', { query, limit, types });
      
      const { data } = await apiClient.get<AutocompleteResponse>('/api/autocomplete', {
        params,
      });

      console.log('✅ Autocomplete response received:', {
        query,
        suggestionsCount: data?.suggestions?.length || 0,
      });

      return data?.suggestions || [];
    } catch (error: any) {
      console.error('Error fetching autocomplete suggestions:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        query,
      });
      // Don't throw error, just return empty array for graceful degradation
      return [];
    }
  },
};

