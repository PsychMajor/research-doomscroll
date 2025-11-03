import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

interface HeaderProps {
  user?: {
    name?: string;
    picture?: string;
  } | null;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="logo">
          📚 Research Doomscroll
        </Link>
        
        <nav className="header-nav">
          <Link to="/" className="nav-link">Feed</Link>
          <Link to="/likes" className="nav-link">Likes</Link>
          <Link to="/folders" className="nav-link">Folders</Link>
          
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
            <Link to="/login" className="login-btn">
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
};
