import React from 'react';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import './Feed.css';

export const Feed: React.FC = () => {
  return (
    <div className="feed-page">
      <div className="feed-header">
        <h1>Research Feed</h1>
        <p className="feed-subtitle">Discover papers tailored to your interests</p>
      </div>

      <div className="search-section">
        <div className="search-form">
          <input
            type="text"
            placeholder="Search papers by topic..."
            className="search-input"
          />
          <button className="search-btn">Search</button>
        </div>
      </div>

      <div className="papers-container">
        <LoadingSpinner text="Ready to search! Enter topics or authors above." />
      </div>
    </div>
  );
};
