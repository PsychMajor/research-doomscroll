import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { foldersApi } from '../api';
import type { CreateFolderRequest, AddPaperToFolderRequest, RemovePaperFromFolderRequest } from '../types/folder';

export const useFolders = () => {
  const queryClient = useQueryClient();

  // Get all folders (from profile)
  const useFoldersList = () => {
    return useQuery({
      queryKey: ['folders'],
      queryFn: async () => {
        const profile = await queryClient.fetchQuery({
          queryKey: ['profile'],
          queryFn: async () => {
            const { profileApi } = await import('../api');
            return profileApi.getProfile();
          },
        });
        return profile.folders;
      },
    });
  };

  // Get single folder
  const useFolder = (folderId: string | null) => {
    return useQuery({
      queryKey: ['folders', folderId],
      queryFn: () => foldersApi.getById(folderId!),
      enabled: !!folderId,
    });
  };

  // Create folder mutation
  const useCreateFolder = () => {
    return useMutation({
      mutationFn: (folder: CreateFolderRequest) => foldersApi.create(folder),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['folders'] });
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Delete folder mutation
  const useDeleteFolder = () => {
    return useMutation({
      mutationFn: (folderId: string) => foldersApi.delete(folderId),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['folders'] });
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Add paper to folder mutation
  const useAddPaperToFolder = () => {
    return useMutation({
      mutationFn: (request: AddPaperToFolderRequest) => foldersApi.addPaper(request),
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries({ queryKey: ['folders'] });
        queryClient.invalidateQueries({ queryKey: ['folders', variables.folder_id] });
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Remove paper from folder mutation
  const useRemovePaperFromFolder = () => {
    return useMutation({
      mutationFn: (request: RemovePaperFromFolderRequest) => foldersApi.removePaper(request),
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries({ queryKey: ['folders'] });
        queryClient.invalidateQueries({ queryKey: ['folders', variables.folder_id] });
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  return {
    useFoldersList,
    useFolder,
    useCreateFolder,
    useDeleteFolder,
    useAddPaperToFolder,
    useRemovePaperFromFolder,
  };
};
