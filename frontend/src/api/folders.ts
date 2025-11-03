import apiClient from './client';
import type {
  CreateFolderRequest,
  AddPaperToFolderRequest,
  RemovePaperFromFolderRequest,
  FolderResponse,
} from '../types/folder';

export const foldersApi = {
  // Create a new folder
  create: async (folder: CreateFolderRequest): Promise<FolderResponse> => {
    const { data } = await apiClient.post('/folders', folder);
    return data;
  },

  // Get folder by ID
  getById: async (folderId: string): Promise<FolderResponse> => {
    const { data } = await apiClient.get(`/folders/${folderId}`);
    return data;
  },

  // Delete folder
  delete: async (folderId: string): Promise<{ status: string }> => {
    const { data } = await apiClient.delete(`/folders/${folderId}`);
    return data;
  },

  // Add paper to folder
  addPaper: async (request: AddPaperToFolderRequest): Promise<{ status: string }> => {
    const { data } = await apiClient.post('/folders/add-paper', request);
    return data;
  },

  // Remove paper from folder
  removePaper: async (request: RemovePaperFromFolderRequest): Promise<{ status: string }> => {
    const { data } = await apiClient.post('/folders/remove-paper', request);
    return data;
  },
};
