import React, { useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import './SidePanel.css';

interface SidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  user?: {
    name?: string;
    picture?: string;
  } | null;
  onLogin: () => void;
  onLogout: () => void;
}

export const SidePanel: React.FC<SidePanelProps> = ({ 
  isOpen, 
  onClose, 
  user, 
  onLogin, 
  onLogout 
}) => {
  const { theme, toggleTheme } = useTheme();

  // Close panel on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when panel is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="side-panel-overlay" 
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      
      {/* Side Panel */}
      <div className={`side-panel ${isOpen ? 'side-panel-open' : ''}`}>
        <div className="side-panel-header">
          <h2 className="side-panel-title">Menu</h2>
          <button 
            className="side-panel-close-btn"
            onClick={onClose}
            aria-label="Close menu"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div className="side-panel-content">
          {/* Dark Mode Toggle */}
          <div className="side-panel-section">
            <div className="side-panel-item">
              <div className="side-panel-item-label">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  {theme === 'light' ? (
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                  ) : (
                    <>
                      <circle cx="12" cy="12" r="5"></circle>
                      <line x1="12" y1="1" x2="12" y2="3"></line>
                      <line x1="12" y1="21" x2="12" y2="23"></line>
                      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                      <line x1="1" y1="12" x2="3" y2="12"></line>
                      <line x1="21" y1="12" x2="23" y2="12"></line>
                      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                    </>
                  )}
                </svg>
                <span>Dark Mode</span>
              </div>
              <button 
                onClick={toggleTheme} 
                className="side-panel-toggle-btn"
                aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
              >
                <div className={`toggle-switch ${theme === 'dark' ? 'toggle-switch-on' : ''}`}>
                  <div className="toggle-switch-slider"></div>
                </div>
              </button>
            </div>
          </div>

          {/* User Section */}
          <div className="side-panel-section">
            {user ? (
              <div className="side-panel-user">
                {user.picture && (
                  <img src={user.picture} alt={user.name || 'User'} className="side-panel-avatar" />
                )}
                <div className="side-panel-user-info">
                  <div className="side-panel-user-name">{user.name || 'User'}</div>
                </div>
              <button 
                onClick={() => {
                  onLogout();
                  onClose();
                }} 
                className="side-panel-logout-btn"
              >
                Logout
              </button>
            </div>
          ) : (
              <button 
                onClick={() => {
                  onLogin();
                  onClose();
                }} 
                className="side-panel-signin-btn"
              >
                Sign in with Google
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

