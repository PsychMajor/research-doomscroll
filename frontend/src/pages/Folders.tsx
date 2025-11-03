import React from 'react';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import './Folders.css';

export const Folders: React.FC = () => {
  return (
    <div className="folders-page">
      <div className="folders-header">
        <h1>📁 My Folders</h1>
        <p className="folders-subtitle">Organize your research papers into collections</p>
        <button className="create-folder-btn">+ Create New Folder</button>
      </div>

      <div className="folders-container">
        <LoadingSpinner text="Loading your folders..." />
      </div>
    </div>
  );
};
