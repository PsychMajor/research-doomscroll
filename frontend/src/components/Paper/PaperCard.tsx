import React, { useState } from 'react';
import type { Paper } from '../../types/paper';
import './PaperCard.css';

interface PaperCardProps {
  paper: Paper;
  likeStatus?: 'liked' | 'disliked' | null;
  onLike?: (paperId: string) => void;
  onDislike?: (paperId: string) => void;
  onAddToFolder?: (paperId: string) => void;
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  likeStatus,
  onLike,
  onDislike,
  onAddToFolder,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatAuthors = (authors: Array<{ name: string; id?: string }>) => {
    if (authors.length === 0) return 'Unknown authors';
    const authorNames = authors.map(a => a.name);
    if (authorNames.length <= 3) return authorNames.join(', ');
    return `${authorNames.slice(0, 3).join(', ')} et al.`;
  };

  return (
    <div className="paper-card">
      <div className="paper-header">
        <h3 className="paper-title">{paper.title}</h3>
      </div>

      <div className="paper-authors">
        {formatAuthors(paper.authors)}
      </div>

      <div className="paper-metadata">
        {paper.year && (
          <span className="paper-date">{paper.year}</span>
        )}
        {paper.citationCount !== undefined && (
          <>
            <span className="metadata-divider">•</span>
            <span className="paper-citations">{paper.citationCount} citations</span>
          </>
        )}
        {paper.venue && (
          <>
            <span className="metadata-divider">•</span>
            <span className="paper-venue">{paper.venue}</span>
          </>
        )}
      </div>

      {paper.abstract && (
        <div className="paper-abstract">
          <p className={isExpanded ? 'expanded' : 'collapsed'}>
            {paper.abstract}
          </p>
          {paper.abstract.length > 300 && (
            <button 
              onClick={() => setIsExpanded(!isExpanded)}
              className="expand-btn"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      )}

      {paper.tldr && (
        <div className="paper-tldr">
          <strong>TL;DR:</strong> {paper.tldr}
        </div>
      )}

      <div className="paper-actions">
        {onLike && (
          <button
            onClick={() => onLike(paper.paperId)}
            className={`action-btn like-btn ${likeStatus === 'liked' ? 'active' : ''}`}
            title="Like"
          >
            {likeStatus === 'liked' ? '❤️' : '🤍'}
          </button>
        )}

        {onDislike && (
          <button
            onClick={() => onDislike(paper.paperId)}
            className={`action-btn dislike-btn ${likeStatus === 'disliked' ? 'active' : ''}`}
            title="Dislike"
          >
            👎
          </button>
        )}

        {onAddToFolder && (
          <button
            onClick={() => onAddToFolder(paper.paperId)}
            className="action-btn folder-btn"
            title="Add to folder"
          >
            ➕
          </button>
        )}

        {paper.url && (
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="action-btn link-btn"
            title="View paper"
          >
            🔗
          </a>
        )}

        {paper.doi && (
          <a
            href={`https://doi.org/${paper.doi}`}
            target="_blank"
            rel="noopener noreferrer"
            className="action-btn doi-btn"
            title="View on DOI"
          >
            DOI
          </a>
        )}
      </div>
    </div>
  );
};
