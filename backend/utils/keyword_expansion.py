"""
GPT-4o-mini powered keyword expansion for search queries
"""
import os
from typing import List, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def expand_keywords(keywords: List[str], api_key: Optional[str] = None, max_expansions: int = 5) -> List[str]:
    """
    Expand a list of keywords by generating 3-5 related academic research terms for each keyword
    
    Args:
        keywords: List of keyword strings to expand (e.g., ["chronic pain"])
        api_key: OpenAI API key (if None, will try to get from OPENAI_API_KEY env var)
        max_expansions: Maximum number of related keywords to generate per input keyword (default: 5)
        
    Returns:
        List of expanded keywords including the original keywords plus related terms
        (e.g., ["chronic pain", "neuropathic pain", "inflammatory pain", "pain management", "chronic pain research"])
    """
    if not keywords or not any(kw.strip() for kw in keywords):
        return []
    
    if not OPENAI_AVAILABLE:
        print("⚠️ OpenAI library not available. Install with: pip install openai")
        return keywords  # Return original keywords if GPT unavailable
    
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY not set. Cannot expand keywords.")
        return keywords  # Return original keywords if API key unavailable
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Combine all keywords into a single query string
        keywords_str = ", ".join(keywords)
        
        system_prompt = """You are a helpful assistant that generates related academic research keywords for search queries.

Given a list of research keywords, generate 3-5 related academic research terms or topics that would help find more comprehensive search results.

CRITICAL RULES:
- Generate terms that are closely related to the input keywords
- Focus on academic/research terminology
- Include synonyms, related concepts, and broader/narrower terms
- Keep terms concise (1-3 words each)
- Return ONLY a JSON object with a "related_keywords" array, no other text

Examples:
- Input: ["chronic pain"] -> {"related_keywords": ["neuropathic pain", "inflammatory pain", "pain management", "chronic pain research", "nociceptive pain"]}
- Input: ["machine learning"] -> {"related_keywords": ["deep learning", "neural networks", "artificial intelligence", "supervised learning", "reinforcement learning"]}
- Input: ["quantum computing"] -> {"related_keywords": ["quantum algorithms", "quantum information", "quantum mechanics", "quantum entanglement", "quantum cryptography"]}

Return format (JSON object only):
{"related_keywords": ["keyword1", "keyword2", "keyword3"]}"""

        user_prompt = f"Generate related academic research keywords for: {keywords_str}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Slightly higher for variety
            max_tokens=200,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        import json
        parsed = json.loads(content)
        
        # Extract related keywords
        related_keywords = parsed.get("related_keywords", [])
        if not isinstance(related_keywords, list):
            related_keywords = []
        
        # Filter and clean related keywords
        related_keywords = [kw.strip() for kw in related_keywords if kw and isinstance(kw, str) and kw.strip()]
        
        # Limit to max_expansions
        related_keywords = related_keywords[:max_expansions]
        
        # Combine original keywords with expanded keywords, removing duplicates
        all_keywords = list(keywords)  # Start with original
        for kw in related_keywords:
            # Add if not already in the list (case-insensitive)
            if not any(existing.lower() == kw.lower() for existing in all_keywords):
                all_keywords.append(kw)
        
        print(f"🔍 Expanded keywords: {keywords} -> {all_keywords}")
        return all_keywords
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing GPT keyword expansion response as JSON: {e}")
        if 'content' in locals():
            print(f"   Response was: {content}")
        return keywords  # Return original keywords on error
    except Exception as e:
        print(f"⚠️ Error calling GPT API for keyword expansion: {e}")
        import traceback
        traceback.print_exc()
        return keywords  # Return original keywords on error

