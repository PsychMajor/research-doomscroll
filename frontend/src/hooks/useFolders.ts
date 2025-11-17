import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { foldersApi } from '../api';
import type { CreateFolderRequest } from '../types/folder';

export const useFolders = () => {
  const queryClient = useQueryClient();

  // Get all folders
  const useFoldersList = () => {
    return useQuery({
      queryKey: ['folders'],
      queryFn: async () => {
        const { foldersApi } = await import('../api');
        return foldersApi.getAll();
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

  // Delete folder mutation with optimistic updates
  const useDeleteFolder = () => {
    return useMutation({
      mutationFn: (folderId: string) => foldersApi.delete(folderId),
      // Optimistically update the cache before the mutation
      onMutate: async (folderId) => {
        // Cancel any outgoing refetches to avoid overwriting optimistic update
        await queryClient.cancelQueries({ queryKey: ['folders'] });
        await queryClient.cancelQueries({ queryKey: ['folders', folderId] });

        // Snapshot the previous value for rollback
        const previousFolders = queryClient.getQueryData(['folders']);
        const previousFolder = queryClient.getQueryData(['folders', folderId]);

        // Optimistically remove the folder from the folders list
        queryClient.setQueryData(['folders'], (old: any) => {
          if (!old || !Array.isArray(old)) return old;
          return old.filter((folder: any) => folder.id !== folderId);
        });

        // Remove the individual folder query data
        queryClient.removeQueries({ queryKey: ['folders', folderId] });

        // Return context with previous values for rollback
        return { previousFolders, previousFolder };
      },
      // If mutation fails, rollback to previous state
      onError: (_err, folderId, context) => {
        if (context?.previousFolders) {
          queryClient.setQueryData(['folders'], context.previousFolders);
        }
        if (context?.previousFolder) {
          queryClient.setQueryData(['folders', folderId], context.previousFolder);
        }
      },
      // Always refetch after error or success to ensure consistency
      onSettled: (_, __, folderId) => {
        queryClient.invalidateQueries({ queryKey: ['folders'] });
        queryClient.invalidateQueries({ queryKey: ['folders', folderId] });
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Add paper to folder mutation with optimistic updates
  const useAddPaperToFolder = () => {
    return useMutation({
      mutationFn: ({ folderId, paperId, paperData }: { folderId: string; paperId: string; paperData: any }) => 
        foldersApi.addPaper(folderId, paperId, paperData),
      // Optimistically update the cache before the mutation
      onMutate: async ({ folderId, paperId, paperData }) => {
        // Cancel any outgoing refetches to avoid overwriting optimistic update
        await queryClient.cancelQueries({ queryKey: ['folders', folderId] });
        await queryClient.cancelQueries({ queryKey: ['folders'] });

        // Snapshot the previous value for rollback
        const previousFolder = queryClient.getQueryData(['folders', folderId]);
        const previousFolders = queryClient.getQueryData(['folders']);

        // Optimistically add the paper to the folder
        queryClient.setQueryData(['folders', folderId], (old: any) => {
          if (!old) return old;
          return {
            ...old,
            papers: [...(old.papers || []), paperData],
          };
        });

        // Optimistically update the folders list
        queryClient.setQueryData(['folders'], (old: any) => {
          if (!old || !Array.isArray(old)) return old;
          return old.map((folder: any) => {
            if (folder.id === folderId) {
              return {
                ...folder,
                papers: [...(folder.papers || []), paperData],
              };
            }
            return folder;
          });
        });

        // Return context with previous values for rollback
        return { previousFolder, previousFolders };
      },
      // If mutation fails, rollback to previous state
      onError: (_err, variables, context) => {
        if (context?.previousFolder) {
          queryClient.setQueryData(['folders', variables.folderId], context.previousFolder);
        }
        if (context?.previousFolders) {
          queryClient.setQueryData(['folders'], context.previousFolders);
        }
      },
      // Always refetch after error or success to ensure consistency
      onSettled: (_, __, variables) => {
        queryClient.invalidateQueries({ queryKey: ['folders', variables.folderId] });
        queryClient.invalidateQueries({ queryKey: ['folders'] });
        queryClient.invalidateQueries({ queryKey: ['profile'] });
      },
    });
  };

  // Remove paper from folder mutation with optimistic updates
  const useRemovePaperFromFolder = () => {
    return useMutation({
      mutationFn: ({ folderId, paperId }: { folderId: string; paperId: string }) => 
        foldersApi.removePaper(folderId, paperId),
      // Optimistically update the cache before the mutation
      onMutate: async ({ folderId, paperId }) => {
        // Cancel any outgoing refetches to avoid overwriting optimistic update
        await queryClient.cancelQueries({ queryKey: ['folders', folderId] });
        await queryClient.cancelQueries({ queryKey: ['folders'] });

        // Snapshot the previous value for rollback
        const previousFolder = queryClient.getQueryData(['folders', folderId]);
        const previousFolders = queryClient.getQueryData(['folders']);

        // Optimistically update the folder
        queryClient.setQueryData(['folders', folderId], (old: any) => {
          if (!old) return old;
          return {
            ...old,
            papers: old.papers?.filter((p: any) => p.paperId !== paperId) || [],
          };
        });

        // Optimistically update the folders list
        queryClient.setQueryData(['folders'], (old: any) => {
          if (!old || !Array.isArray(old)) return old;
          return old.map((folder: any) => {
            if (folder.id === folderId) {
              return {
                ...folder,
                papers: folder.papers?.filter((p: any) => p.paperId !== paperId) || [],
              };
            }
            return folder;
          });
        });

        // Return context with previous values for rollback
        return { previousFolder, previousFolders };
      },
      // If mutation fails, rollback to previous state
      onError: (_err, variables, context) => {
        if (context?.previousFolder) {
          queryClient.setQueryData(['folders', variables.folderId], context.previousFolder);
        }
        if (context?.previousFolders) {
          queryClient.setQueryData(['folders'], context.previousFolders);
        }
      },
      // Always refetch after error or success to ensure consistency
      onSettled: (_, __, variables) => {
        queryClient.invalidateQueries({ queryKey: ['folders', variables.folderId] });
        queryClient.invalidateQueries({ queryKey: ['folders'] });
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
