import React, { useEffect, useState } from 'react';
import type { Paper } from '../../types/paper';
import { renderHtml, containsHtml } from '../../utils/htmlSanitizer';
import './PaperCard.css';

interface PaperCardProps {
  paper: Paper;
  likeStatus?: 'liked' | 'disliked' | null;
  addedToFolder?: boolean;
  onLike?: (paperId: string) => void;
  onDislike?: (paperId: string) => void;
  onAddToFolder?: (paperId: string) => void;
  onRemove?: (paperId: string) => void;
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  likeStatus,
  addedToFolder = false,
  onLike,
  onDislike,
  onAddToFolder,
  onRemove,
}) => {
  const [showAbstract, setShowAbstract] = useState(false);
  const [showAllAuthors, setShowAllAuthors] = useState(false);

  useEffect(() => {
    setShowAllAuthors(false);
  }, [paper.paperId]);

  const renderAuthors = (authors: Array<{ name: string; id?: string }>) => {
    if (authors.length === 0) {
      return <span>Unknown authors</span>;
    }

    const authorNames = authors.map(a => a.name);

    if (authorNames.length <= 4) {
      return <span>{authorNames.join(', ')}</span>;
    }

    if (showAllAuthors) {
      return (
        <>
          <span>{authorNames.join(', ')}</span>
          <button
            type="button"
            className="authors-toggle"
            onClick={() => setShowAllAuthors(false)}
          >
            less
          </button>
        </>
      );
    }

    const firstAuthors = authorNames.slice(0, 2).join(', ');
    const lastAuthors = authorNames.slice(-2).join(', ');
    const hiddenCount = authorNames.length - 4;

    return (
      <>
        <span>{firstAuthors}, </span>
        <button
          type="button"
          className="authors-toggle"
          onClick={() => setShowAllAuthors(true)}
        >
          +{hiddenCount} authors
        </button>
        <span> {lastAuthors}</span>
      </>
    );
  };

  const getPublisherUrl = () => {
    if (paper.url) return paper.url;
    if (paper.doi) return `https://doi.org/${paper.doi}`;
    return null;
  };

  const handleLike = () => {
    if (onLike) {
      onLike(paper.paperId);
    }
  };

  const handleDislike = () => {
    if (onDislike) {
      onDislike(paper.paperId);
    }
  };

  const handleRemove = () => {
    if (onRemove) {
      onRemove(paper.paperId);
    }
  };

  // Render title with HTML support
  const renderTitle = () => {
    if (containsHtml(paper.title)) {
      return <h3 className="paper-title" dangerouslySetInnerHTML={renderHtml(paper.title)} />;
    }
    return <h3 className="paper-title">{paper.title}</h3>;
  };

  // Render TL;DR with HTML support
  const renderTldr = () => {
    if (!paper.tldr) return null;
    
    if (containsHtml(paper.tldr)) {
      return (
        <div className="paper-tldr">
          <div className="tldr-content">
            <strong className="tldr-label">TL;DR:</strong>
            <span className="tldr-text" dangerouslySetInnerHTML={renderHtml(paper.tldr)} />
          </div>
        </div>
      );
    }
    
    return (
      <div className="paper-tldr">
        <div className="tldr-content">
          <strong className="tldr-label">TL;DR:</strong>
          <span className="tldr-text">{paper.tldr}</span>
        </div>
      </div>
    );
  };

  // Render abstract with HTML support
  const renderAbstract = () => {
    if (!paper.abstract) {
      return (
        <div className="paper-abstract-expanded">
          <p className="no-abstract-message">No abstract available</p>
        </div>
      );
    }
    
    if (containsHtml(paper.abstract)) {
      return (
        <div className="paper-abstract-expanded">
          <div 
            className="abstract-content"
            dangerouslySetInnerHTML={renderHtml(paper.abstract)} 
          />
        </div>
      );
    }
    
    // For plain text, split by newlines and render as paragraphs
    const paragraphs = paper.abstract.split('\n').filter(p => p.trim());
    if (paragraphs.length > 1) {
      return (
        <div className="paper-abstract-expanded">
          {paragraphs.map((para, idx) => (
            <p key={idx}>{para.trim()}</p>
          ))}
        </div>
      );
    }
    
    return (
      <div className="paper-abstract-expanded">
        <p>{paper.abstract}</p>
      </div>
    );
  };

  const hasMetadata = Boolean(paper.year || paper.venue);

  return (
    <div className="paper-card">
      {renderTitle()}

      <div className="paper-authors-row">
        <div className="paper-authors">
          {renderAuthors(paper.authors)}
        </div>

        {hasMetadata && (
          <div className="paper-metadata-wrapper">
            <span className="authors-metadata-dot" aria-hidden="true"></span>
            <div className="paper-metadata">
              {paper.year && (
                <span className="paper-year">{paper.year}</span>
              )}
              {paper.venue && (
                <>
                  {paper.year && <span className="metadata-separator" aria-hidden="true"></span>}
                  <span className="paper-venue">{paper.venue}</span>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {renderTldr()}

      <div className="paper-links">
        <button
          onClick={() => setShowAbstract(!showAbstract)}
          className={`link-btn abstract-link ${showAbstract ? 'expanded' : ''}`}
        >
          <span className={`link-icon ${showAbstract ? 'rotated' : ''}`}>▶</span>
          Abstract
        </button>
      </div>

      {showAbstract && renderAbstract()}

      <div className="paper-actions">
        <div className="paper-actions-left">
          {onRemove && (
            <button
              onClick={handleRemove}
              className="action-btn remove-btn"
            >
              Remove
            </button>
          )}
          {onLike && (
            <button
              onClick={handleLike}
              className={`action-btn like-btn ${likeStatus === 'liked' ? 'active' : ''}`}
            >
              {likeStatus === 'liked' ? 'Liked!' : 'Like'}
            </button>
          )}
          {onDislike && (
            <button
              onClick={handleDislike}
              className={`action-btn pass-btn ${likeStatus === 'disliked' ? 'active' : ''}`}
            >
              Pass
            </button>
          )}
          {onAddToFolder && (
            <button
              onClick={() => onAddToFolder(paper.paperId)}
              className={`action-btn add-btn ${addedToFolder ? 'added' : ''}`}
            >
              {addedToFolder ? 'Added' : 'Add'}
            </button>
          )}
        </div>
        {getPublisherUrl() && (
          <a
            href={getPublisherUrl()!}
            target="_blank"
            rel="noopener noreferrer"
            className="publisher-link-action"
          >
            URL
            <span className="external-icon">↗</span>
          </a>
        )}
      </div>
    </div>
  );
};
