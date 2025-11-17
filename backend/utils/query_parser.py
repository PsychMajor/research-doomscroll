"""
Query parser utility for extracting keywords and authors from natural language search queries
"""
import re
from typing import Dict, List, Tuple


def parse_search_query(query: str) -> Dict[str, List[str]]:
    """
    Parse a natural language search query to extract keywords and authors
    
    Handles various formats:
    - "papers about machine learning by John Smith"
    - "John Smith, Jane Doe neural networks"
    - "quantum computing papers"
    - "pain research by Michael J. Iadarola"
    - "machine learning, deep learning by John Smith and Jane Doe"
    
    Args:
        query: Natural language search query string
        
    Returns:
        Dictionary with 'keywords' and 'authors' lists
    """
    if not query or not query.strip():
        return {"keywords": [], "authors": []}
    
    query = query.strip()
    
    # Pattern 1: Look for explicit author markers: "by [authors]" or "from [authors]"
    # This handles: "machine learning by John Smith" or "papers from Jane Doe"
    # Also handles: "by John Smith machine learning" (keywords after author)
    author_marker_pattern = r'\b(?:by|from|author|authors?)\s+'
    author_marker_match = re.search(author_marker_pattern, query, re.IGNORECASE)
    
    if author_marker_match:
        # Split query at the marker
        before_marker = query[:author_marker_match.start()].strip()
        after_marker = query[author_marker_match.end():].strip()
        
        # Case 1: Keywords before marker, authors after
        # Example: "machine learning by John Smith"
        if before_marker:
            authors = _extract_authors(after_marker)
            keywords = _extract_keywords(before_marker)
            # Clean up keywords
            keywords_clean = []
            for kw in keywords:
                kw = re.sub(r'\b(?:papers?|research|articles?|studies?)\s+(?:about|on|regarding|in)\s+', '', kw, flags=re.IGNORECASE)
                kw = kw.strip()
                if kw:
                    keywords_clean.append(kw)
            return {"keywords": keywords_clean, "authors": authors}
        
        # Case 2: No keywords before marker, check if keywords are after authors
        # Example: "by John Smith machine learning"
        words_after = after_marker.split()
        
        # Look for the first lowercase word - that's likely the start of keywords
        # Author names are capitalized, so lowercase = keywords
        split_idx = None
        for i, word in enumerate(words_after):
            # Skip first 2 words (author name parts are capitalized)
            if i >= 2 and word and word[0].islower():
                split_idx = i
                break
        
        # If we found a split point, separate authors and keywords
        if split_idx:
            author_part = ' '.join(words_after[:split_idx])
            keyword_part = ' '.join(words_after[split_idx:])
            authors = _extract_authors(author_part)
            keywords = _extract_keywords(keyword_part) if keyword_part else []
            return {"keywords": keywords, "authors": authors}
        
        # No split found, treat everything after marker as authors
        authors = _extract_authors(after_marker)
        return {"keywords": [], "authors": authors}
    
    # Pattern 2: Look for comma-separated capitalized names at the start
    # This handles: "John Smith, Jane Doe neural networks"
    # or "Michael J. Iadarola, Matthew R. Sapio pain research"
    start_authors_pattern = r'^((?:[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:\s*,\s*)?)+)'
    start_authors_match = re.match(start_authors_pattern, query)
    
    if start_authors_match:
        author_part = start_authors_match.group(1).strip()
        keyword_part = query[start_authors_match.end():].strip()
        
        # Clean up keyword part
        keyword_part = re.sub(r'^\s*(?:about|on|regarding|in|papers?|research|articles?)\s+', '', keyword_part, flags=re.IGNORECASE)
        keyword_part = keyword_part.strip()
        
        authors = _extract_authors(author_part)
        keywords = _extract_keywords(keyword_part) if keyword_part else []
        
        return {"keywords": keywords, "authors": authors}
    
    # Pattern 3: Look for "and" or "&" connecting author names
    # This handles: "John Smith and Jane Doe machine learning"
    and_authors_pattern = r'^((?:[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)+))'
    and_authors_match = re.match(and_authors_pattern, query)
    
    if and_authors_match:
        author_part = and_authors_match.group(1).strip()
        keyword_part = query[and_authors_match.end():].strip()
        
        keyword_part = re.sub(r'^\s*(?:about|on|regarding|in|papers?|research|articles?)\s+', '', keyword_part, flags=re.IGNORECASE)
        keyword_part = keyword_part.strip()
        
        authors = _extract_authors(author_part)
        keywords = _extract_keywords(keyword_part) if keyword_part else []
        
        return {"keywords": keywords, "authors": authors}
    
    # Pattern 4: No clear author pattern, treat everything as keywords
    # But still try to extract any capitalized names that might be authors
    # This is more conservative - only extract if we're confident
    
    # Look for capitalized name patterns in the query
    potential_authors = []
    remaining_query = query
    
    # Find all potential author patterns (First Last or First Middle Last)
    author_name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
    potential_matches = re.finditer(author_name_pattern, query)
    
    for match in potential_matches:
        name = match.group(1)
        # Check if it's likely an author name (not a keyword like "Machine Learning")
        if _is_likely_author_name(name):
            potential_authors.append(name)
            # Remove from remaining query
            remaining_query = remaining_query.replace(name, '', 1)
    
    # Clean up remaining query
    remaining_query = re.sub(r'\b(?:papers?|research|articles?|studies?)\s+(?:about|on|regarding|in)\s+', '', remaining_query, flags=re.IGNORECASE)
    remaining_query = re.sub(r'\s+', ' ', remaining_query).strip()
    
    keywords = _extract_keywords(remaining_query) if remaining_query else []
    
    return {"keywords": keywords, "authors": potential_authors}


def _extract_authors(author_string: str) -> List[str]:
    """
    Extract individual author names from a string
    
    Handles:
    - "John Smith"
    - "John Smith, Jane Doe"
    - "John Smith and Jane Doe"
    - "John Smith & Jane Doe"
    - "Michael J. Iadarola, Matthew R. Sapio"
    """
    if not author_string:
        return []
    
    # Split by comma, "and", or "&"
    author_string = re.sub(r'\s+and\s+', ', ', author_string, flags=re.IGNORECASE)
    author_string = re.sub(r'\s+&\s+', ', ', author_string)
    
    authors = []
    for part in author_string.split(','):
        part = part.strip()
        if part:
            authors.append(part)
    
    return authors


def _extract_keywords(keyword_string: str) -> List[str]:
    """
    Extract keywords from a string
    
    Handles:
    - "machine learning, deep learning"
    - "quantum computing"
    - "pain, spinal cord injury"
    """
    if not keyword_string:
        return []
    
    # Split by comma or treat as single keyword phrase
    keywords = []
    for part in keyword_string.split(','):
        part = part.strip()
        if part:
            keywords.append(part)
    
    return keywords


def _is_likely_author_name(name: str) -> bool:
    """
    Determine if a capitalized string is likely an author name vs a keyword
    
    Author names typically:
    - Have 2-3 words (First Last or First Middle Last)
    - May have middle initial (e.g., "Michael J. Iadarola")
    - Don't contain common keyword words
    
    Keywords that might be capitalized:
    - "Machine Learning", "Deep Learning", "Quantum Computing"
    - Single capitalized words are usually not authors
    """
    # Common keyword patterns that are capitalized
    keyword_patterns = [
        r'\b(?:Machine|Deep|Neural|Artificial|Quantum|Classical|Statistical)\s+',
        r'\b(?:Learning|Network|Computing|Intelligence|Analysis)\b',
    ]
    
    for pattern in keyword_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return False
    
    # Check word count - author names typically have 2-4 words
    words = name.split()
    if len(words) < 2 or len(words) > 4:
        return False
    
    # Check if it looks like a name pattern (First Last or First Middle Last)
    # First word should be capitalized, last word should be capitalized
    if not (words[0][0].isupper() and words[-1][0].isupper()):
        return False
    
    return True

