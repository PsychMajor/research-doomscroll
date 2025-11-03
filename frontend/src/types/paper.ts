// Paper types matching backend models
export interface Paper {
  paperId: string;
  title: string;
  authors: Array<{ name: string; id?: string }>;
  year?: number;
  abstract?: string | null;
  doi?: string | null;
  citationCount?: number;
  url?: string | null;
  venue?: string | null;
  tldr?: string | null;
  source?: string;
}

export interface SearchParams {
  topics?: string;  // comma-separated
  authors?: string; // comma-separated
  sortBy?: 'recency' | 'relevance';
  page?: number;
}

export interface SearchResponse {
  papers: Paper[];
  total: number;
  has_more: boolean;
}
