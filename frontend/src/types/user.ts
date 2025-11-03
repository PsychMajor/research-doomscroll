// User types matching backend models
export interface User {
  id?: string;
  email: string;
  name?: string | null;
  picture?: string | null;
  research_interests?: string[];
  session_id?: string | null;
  last_login?: string | null;
}

export interface UserProfileResponse {
  user: User;
  liked_papers: string[];
  disliked_papers: string[];
  folders: Folder[];
}

export interface Folder {
  id: string;
  name: string;
  description?: string | null;
  papers: string[];
  created_at: string;
}
