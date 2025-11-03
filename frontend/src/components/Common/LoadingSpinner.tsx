import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  text?: string;
  size?: 'small' | 'medium' | 'large';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  text = 'Loading...', 
  size = 'medium' 
}) => {
  return (
    <div className={`loading-spinner-container ${size}`}>
      <div className="spinner"></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};
