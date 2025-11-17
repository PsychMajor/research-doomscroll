import React from 'react';
import { Link } from 'react-router-dom';
import type { FolderResponse } from '../../types/folder';
import './FolderCard.css';

interface FolderCardProps {
  folder: FolderResponse;
  onDelete?: (folderId: string) => void;
}

export const FolderCard: React.FC<FolderCardProps> = ({ folder, onDelete }) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Recently';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return 'Recently';
    }
  };

  const paperCount = folder.papers?.length || 0;

  return (
    <div className="folder-card">
      <div className="folder-header">
        <Link to={`/folders/${folder.id}`} className="folder-name">
          {folder.name}
        </Link>
        {onDelete && folder.id !== 'likes' && (
          <button
            onClick={() => onDelete(folder.id)}
            className="delete-folder-btn"
            title="Delete folder"
          >
            ×
          </button>
        )}
      </div>

      {folder.description && (
        <p className="folder-description">{folder.description}</p>
      )}

      <div className="folder-metadata">
        <span className="paper-count">
          {paperCount} {paperCount === 1 ? 'paper' : 'papers'}
        </span>
        {folder.created_at && (
          <span className="folder-date">Created {formatDate(folder.created_at)}</span>
        )}
      </div>
    </div>
  );
};
