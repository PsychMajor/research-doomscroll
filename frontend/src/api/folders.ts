import apiClient from './client';
import type {
  CreateFolderRequest,
  AddPaperToFolderRequest,
  RemovePaperFromFolderRequest,
  FolderResponse,
} from '../types/folder';

import type { Paper } from '../types/paper';

export const foldersApi = {
  // Get all folders
  getAll: async (): Promise<FolderResponse[]> => {
    const { data } = await apiClient.get('/api/folders');
    return data;
  },

  // Create a new folder
  create: async (folder: CreateFolderRequest): Promise<FolderResponse> => {
    const { data } = await apiClient.post('/api/folders', folder);
    return data;
  },

  // Get folder by ID
  getById: async (folderId: string): Promise<FolderResponse> => {
    const { data } = await apiClient.get(`/api/folders/${folderId}`);
    return data;
  },

  // Delete folder
  delete: async (folderId: string): Promise<{ status: string }> => {
    const { data } = await apiClient.delete(`/api/folders/${folderId}`);
    return data;
  },

  // Add paper to folder
  addPaper: async (folderId: string, paperId: string, paperData: Paper): Promise<{ status: string }> => {
    const { data } = await apiClient.post(`/api/folders/${folderId}/papers`, {
      paper_id: paperId,
      paper_data: paperData,
    });
    return data;
  },

  // Remove paper from folder
  removePaper: async (folderId: string, paperId: string): Promise<{ status: string }> => {
    const { data } = await apiClient.delete(`/api/folders/${folderId}/papers/${paperId}`);
    return data;
  },
};
