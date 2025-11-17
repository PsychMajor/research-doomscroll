import React, { useState } from 'react';
import './FolderModal.css';

interface Folder {
  id: string;
  name: string;
  description?: string | null;
}

interface FolderModalProps {
  isOpen: boolean;
  onClose: () => void;
  folders: Folder[];
  onSelectFolder: (folderId: string) => void;
  onCreateFolder: (name: string, description?: string) => void;
}

export const FolderModal: React.FC<FolderModalProps> = ({
  isOpen,
  onClose,
  folders,
  onSelectFolder,
  onCreateFolder,
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderDescription, setNewFolderDescription] = useState('');

  if (!isOpen) return null;

  const handleCreateFolder = () => {
    if (newFolderName.trim()) {
      onCreateFolder(newFolderName.trim(), newFolderDescription.trim() || undefined);
      setNewFolderName('');
      setNewFolderDescription('');
      setIsCreating(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="folder-modal-backdrop" onClick={handleBackdropClick}>
      <div className="folder-modal">
        <div className="modal-header">
          <h2>Add to Folder</h2>
          <button onClick={onClose} className="close-modal-btn">
            ×
          </button>
        </div>

        <div className="modal-content">
          {!isCreating ? (
            <>
              <p className="folder-instruction">Select a folder for this paper:</p>
              
              <div className="folder-list">
                {folders.length === 0 ? (
                  <p className="no-folders-message">
                    No folders yet. Create your first folder!
                  </p>
                ) : (
                  folders.map((folder) => (
                    <button
                      key={folder.id}
                      onClick={() => {
                        onSelectFolder(folder.id);
                        onClose();
                      }}
                      className="folder-option"
                    >
                      <svg className="folder-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                      </svg>
                      <div className="folder-info">
                        <span className="folder-option-name">{folder.name}</span>
                        {folder.description && (
                          <span className="folder-option-description">
                            {folder.description}
                          </span>
                        )}
                      </div>
                    </button>
                  ))
                )}
              </div>

              <button
                onClick={() => setIsCreating(true)}
                className="create-folder-btn"
              >
                + Create New Folder
              </button>
            </>
          ) : (
            <div className="create-folder-form">
              <input
                type="text"
                placeholder="Folder name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                className="folder-name-input"
                autoFocus
              />
              <textarea
                placeholder="Description (optional)"
                value={newFolderDescription}
                onChange={(e) => setNewFolderDescription(e.target.value)}
                className="folder-description-input"
                rows={3}
              />
              <div className="form-actions">
                <button onClick={() => setIsCreating(false)} className="cancel-btn">
                  Cancel
                </button>
                <button
                  onClick={handleCreateFolder}
                  className="confirm-create-btn"
                  disabled={!newFolderName.trim()}
                >
                  Create
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
