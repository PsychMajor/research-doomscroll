import React, { useEffect, useRef } from 'react';
import type { AutocompleteSuggestion } from '../../api/autocomplete';
import './AutocompleteDropdown.css';

interface AutocompleteDropdownProps {
  /**
   * List of autocomplete suggestions to display
   */
  suggestions: AutocompleteSuggestion[];
  /**
   * Whether the dropdown is visible
   */
  visible: boolean;
  /**
   * Currently highlighted suggestion index
   */
  highlightedIndex: number;
  /**
   * Callback when a suggestion is selected
   */
  onSelect: (suggestion: AutocompleteSuggestion) => void;
  /**
   * Callback when highlighted index changes
   */
  onHighlightChange: (index: number) => void;
  /**
   * Loading state
   */
  isLoading?: boolean;
  /**
   * Whether to show empty state message when no suggestions are found
   */
  showEmptyState?: boolean;
  /**
   * Current query string (for empty state message)
   */
  query?: string;
}

/**
 * Type labels mapping
 */
const TYPE_LABELS: Record<string, string> = {
  paper: 'Paper',
  author: 'Author',
  journal: 'Journal',
  institution: 'Institution',
  topic: 'Topic',
};

/**
 * AutocompleteDropdown component for displaying search suggestions
 * 
 * Features:
 * - Google-like dropdown styling
 * - Keyboard navigation (arrows, Enter, Escape)
 * - Mouse hover highlighting
 * - Type icons/badges
 * - Smooth animations
 */
export const AutocompleteDropdown: React.FC<AutocompleteDropdownProps> = ({
  suggestions,
  visible,
  highlightedIndex,
  onSelect,
  onHighlightChange,
  isLoading = false,
  showEmptyState = false,
  query = '',
}) => {
  const dropdownRef = useRef<HTMLDivElement>(null);
  const highlightedItemRef = useRef<HTMLLIElement>(null);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && highlightedItemRef.current) {
      highlightedItemRef.current.scrollIntoView({
        block: 'nearest',
        behavior: 'smooth',
      });
    }
  }, [highlightedIndex]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!visible || suggestions.length === 0) {
      return;
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          onHighlightChange(
            highlightedIndex < suggestions.length - 1
              ? highlightedIndex + 1
              : highlightedIndex
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          onHighlightChange(
            highlightedIndex > 0 ? highlightedIndex - 1 : -1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
            onSelect(suggestions[highlightedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onHighlightChange(-1);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [visible, suggestions, highlightedIndex, onSelect, onHighlightChange]);

  // Don't render if not visible
  if (!visible) {
    return null;
  }
  
  // Show empty state if no suggestions and not loading (and showEmptyState is true)
  const shouldShowEmptyState = showEmptyState && !isLoading && suggestions.length === 0 && query.trim().length >= 2;

  // Get type label
  const getTypeLabel = (type: string) => TYPE_LABELS[type] || type;

  return (
    <div
      ref={dropdownRef}
      className={`autocomplete-dropdown ${visible ? 'visible' : ''}`}
      role="listbox"
      aria-label="Search suggestions"
    >
      {isLoading && (
        <div className="autocomplete-loading">
          <span>Loading suggestions...</span>
        </div>
      )}
      {shouldShowEmptyState && (
        <div className="autocomplete-empty">
          <span>No suggestions found for "{query}"</span>
        </div>
      )}
      {!isLoading && !shouldShowEmptyState && suggestions.length > 0 && (
        <ul className="autocomplete-suggestions">
          {suggestions.map((suggestion, index) => (
            <li
              key={`${suggestion.type}-${index}-${suggestion.text}`}
              ref={index === highlightedIndex ? highlightedItemRef : null}
              className={`autocomplete-suggestion ${
                index === highlightedIndex ? 'highlighted' : ''
              }`}
              role="option"
              aria-selected={index === highlightedIndex}
              onMouseEnter={() => onHighlightChange(index)}
              onClick={() => onSelect(suggestion)}
            >
              <span className="autocomplete-text">{suggestion.text}</span>
              <span className="autocomplete-type-label">
                {getTypeLabel(suggestion.type)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

