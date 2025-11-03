// Paper types matching backend models
export interface Paper {
  id: string;
  title: string;
  authors: string[];
  publication_date: string;
  abstract: string;
  doi?: string | null;
  cited_by_count?: number;
  openalex_url?: string | null;
  pdf_url?: string | null;
  concepts?: string[];
  relevance_score?: number;
  like_status?: string | null;
}

export interface SearchParams {
  query: string;
  concepts?: string[];
  year_min?: number;
  year_max?: number;
  cited_by_min?: number;
  sort_by?: 'relevance' | 'cited_by_count' | 'publication_date';
  offset?: number;
  limit?: number;
}

export interface SearchResponse {
  papers: Paper[];
  total: number;
  has_more: boolean;
}
