import type { Paper } from './paper';

// Folder types matching backend models
export interface CreateFolderRequest {
  name: string;
  description?: string | null;
}

export interface AddPaperToFolderRequest {
  folder_id: string;
  paper_id: string;
}

export interface RemovePaperFromFolderRequest {
  folder_id: string;
  paper_id: string;
}

export interface FolderResponse {
  id: string;
  name: string;
  description?: string | null;
  papers: Paper[]; // Array of full paper objects
  created_at?: string;
}
