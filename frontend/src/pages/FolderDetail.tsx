import React from 'react';
import { useParams } from 'react-router-dom';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import './FolderDetail.css';

export const FolderDetail: React.FC = () => {
  const { folderId } = useParams<{ folderId: string }>();

  return (
    <div className="folder-detail-page">
      <div className="folder-detail-header">
        <h1>📁 Folder</h1>
        <p className="folder-id">ID: {folderId}</p>
      </div>

      <div className="papers-container">
        <LoadingSpinner text="Loading papers in this folder..." />
      </div>
    </div>
  );
};
