// User types matching backend models
export interface User {
  id?: string | number;
  email: string;
  name?: string | null;
  picture?: string | null;
  research_interests?: string[];
  session_id?: string | null;
  last_login?: string | null;
}

// UserProfile matches backend UserProfile model
export interface UserProfileResponse {
  topics: string[];
  authors: string[];
  folders: Folder[];
}

export interface Folder {
  id: string;
  name: string;
  description?: string | null;
  papers: any[]; // Array of paper objects
  created_at?: string;
}
