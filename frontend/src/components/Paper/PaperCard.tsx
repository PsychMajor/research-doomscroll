import React, { useState } from 'react';
import type { Paper } from '../../types/paper';
import './PaperCard.css';

interface PaperCardProps {
  paper: Paper;
  likeStatus?: 'liked' | 'disliked' | null;
  onLike: (paperId: string) => void;
  onDislike: (paperId: string) => void;
  onAddToFolder: (paperId: string) => void;
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  likeStatus,
  onLike,
  onDislike,
  onAddToFolder,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatAuthors = (authors: string[]) => {
    if (authors.length === 0) return 'Unknown authors';
    if (authors.length <= 3) return authors.join(', ');
    return `${authors.slice(0, 3).join(', ')} et al.`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
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
        <span className="paper-date">{formatDate(paper.publication_date)}</span>
        {paper.cited_by_count !== undefined && (
          <>
            <span className="metadata-divider">•</span>
            <span className="paper-citations">{paper.cited_by_count} citations</span>
          </>
        )}
        {paper.relevance_score && (
          <>
            <span className="metadata-divider">•</span>
            <span className="paper-relevance">
              Relevance: {Math.round(paper.relevance_score * 100)}%
            </span>
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

      {paper.concepts && paper.concepts.length > 0 && (
        <div className="paper-concepts">
          {paper.concepts.slice(0, 5).map((concept, idx) => (
            <span key={idx} className="concept-tag">
              {concept}
            </span>
          ))}
        </div>
      )}

      <div className="paper-actions">
        <button
          onClick={() => onLike(paper.id)}
          className={`action-btn like-btn ${likeStatus === 'liked' ? 'active' : ''}`}
          title="Like"
        >
          {likeStatus === 'liked' ? '❤️' : '🤍'}
        </button>

        <button
          onClick={() => onDislike(paper.id)}
          className={`action-btn dislike-btn ${likeStatus === 'disliked' ? 'active' : ''}`}
          title="Dislike"
        >
          👎
        </button>

        <button
          onClick={() => onAddToFolder(paper.id)}
          className="action-btn folder-btn"
          title="Add to folder"
        >
          ➕
        </button>

        {paper.openalex_url && (
          <a
            href={paper.openalex_url}
            target="_blank"
            rel="noopener noreferrer"
            className="action-btn link-btn"
            title="View on OpenAlex"
          >
            🔗
          </a>
        )}

        {paper.pdf_url && (
          <a
            href={paper.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="action-btn pdf-btn"
            title="Download PDF"
          >
            📄
          </a>
        )}
      </div>
    </div>
  );
};
