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
  papers: string[];
  created_at: string;
}
