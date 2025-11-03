import React from 'react';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import './Likes.css';

export const Likes: React.FC = () => {
  return (
    <div className="likes-page">
      <div className="likes-header">
        <h1>❤️ Liked Papers</h1>
        <p className="likes-subtitle">Your collection of favorite research papers</p>
      </div>

      <div className="papers-container">
        <LoadingSpinner text="Loading your liked papers..." />
      </div>
    </div>
  );
};
