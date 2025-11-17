import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';
import './Header.css';

interface HeaderProps {
  user?: {
    name?: string;
    picture?: string;
  } | null;
  onLogin: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogin, onLogout }) => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  
  return (
    <>
      <div className="header-top">
        <div className="header-top-content">
          <div className="header-title-section">
            <h1 className="app-title">Pando</h1>
            <p className="app-subtitle">Keep up with the world's literature</p>
          </div>
          <div className="header-divider"></div>
          <div className="header-actions">
          <button 
            onClick={toggleTheme} 
            className="theme-toggle-btn"
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
            )}
          </button>
          {user ? (
            <div className="user-menu">
              {user.picture && (
                <img src={user.picture} alt={user.name || 'User'} className="user-avatar" />
              )}
              <span className="user-name">{user.name || 'User'}</span>
              <button onClick={onLogout} className="logout-btn">
                Logout
              </button>
            </div>
          ) : (
            <button onClick={onLogin} className="signin-btn">
              Sign in with Google
            </button>
          )}
          </div>
        </div>
      </div>
    </>
  );
};
