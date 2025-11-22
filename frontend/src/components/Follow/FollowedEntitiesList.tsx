import React from 'react';
import { useFollows, useUnfollowEntity } from '../../hooks/useFollows';
import type { Follow, FollowEntityType } from '../../api/follows';
import './FollowedEntitiesList.css';

export const FollowedEntitiesList: React.FC = () => {
  const { data: follows, isLoading } = useFollows();
  const unfollowMutation = useUnfollowEntity();

  const handleUnfollow = (follow: Follow) => {
    unfollowMutation.mutate({
      entityType: follow.type,
      entityId: follow.entityId,
    });
  };

  const typeLabels: Record<FollowEntityType, string> = {
    author: 'Author',
    institution: 'Institution',
    topic: 'Topic',
    source: 'Journal',
    custom: 'Custom',
  };

  if (isLoading) {
    return (
      <div className="followed-entities-list">
        <div className="loading">Loading follows...</div>
      </div>
    );
  }

  if (!follows || follows.length === 0) {
    return (
      <div className="followed-entities-list">
        <div className="empty-state">
          <p>You're not following anyone yet.</p>
          <p className="hint">Use the search above to find and follow authors, institutions, topics, or journals.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="followed-entities-list">
      {follows.map((follow) => (
        <div key={follow.id} className="follow-bubble">
          <span className="follow-bubble-text">
            <span className="follow-bubble-category">
              {follow.type === 'custom' ? 'Custom' : typeLabels[follow.type]}:
            </span> {follow.entityName}
          </span>
          <button
            className="follow-bubble-unfollow"
            onClick={() => handleUnfollow(follow)}
            disabled={unfollowMutation.isPending}
            aria-label={`Unfollow ${follow.entityName}`}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
};

