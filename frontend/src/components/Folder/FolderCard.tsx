import React from 'react';
import { Link } from 'react-router-dom';
import './FolderCard.css';

interface FolderCardProps {
  folder: {
    id: string;
    name: string;
    description?: string | null;
    papers: string[];
    created_at: string;
  };
  onDelete: (folderId: string) => void;
}

export const FolderCard: React.FC<FolderCardProps> = ({ folder, onDelete }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <div className="folder-card">
      <div className="folder-header">
        <Link to={`/folders/${folder.id}`} className="folder-name">
          📁 {folder.name}
        </Link>
        <button
          onClick={() => onDelete(folder.id)}
          className="delete-folder-btn"
          title="Delete folder"
        >
          ×
        </button>
      </div>

      {folder.description && (
        <p className="folder-description">{folder.description}</p>
      )}

      <div className="folder-metadata">
        <span className="paper-count">
          {folder.papers.length} {folder.papers.length === 1 ? 'paper' : 'papers'}
        </span>
        <span className="folder-date">Created {formatDate(folder.created_at)}</span>
      </div>
    </div>
  );
};
