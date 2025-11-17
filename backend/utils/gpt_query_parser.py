"""
GPT-4o-mini powered query parser for extracting entities from search queries
"""
import os
import json
from typing import Dict, List, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def parse_search_query_with_gpt(query: str, api_key: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Parse a search query using GPT-4o-mini to extract keywords, authors, years, and institutions
    
    Args:
        query: Natural language search query string
        api_key: OpenAI API key (if None, will try to get from OPENAI_API_KEY env var)
        
    Returns:
        Dictionary with 'keywords', 'authors', 'years', and 'institutions' lists
    """
    if not query or not query.strip():
        return {"keywords": [], "authors": [], "years": [], "institutions": []}
    
    if not OPENAI_AVAILABLE:
        print("⚠️ OpenAI library not available. Install with: pip install openai")
        return {"keywords": [], "authors": [], "years": [], "institutions": []}
    
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY not set. Cannot use GPT parser.")
        return {"keywords": [], "authors": [], "years": [], "institutions": []}
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Create a structured prompt for entity extraction
        system_prompt = """You are a helpful assistant that extracts structured information from academic search queries.

Extract the following entities from the user's query:
1. **Keywords/Topics**: Research topics, subject areas, or keywords (e.g., "machine learning", "quantum computing", "pain research")
2. **Authors**: Person names (e.g., "John Smith", "Michael J. Iadarola")
3. **Years**: Publication years, year ranges, or relative years (e.g., "2020", "2020-2023", ">2020", "after 2020")
4. **Institutions**: Universities, research institutions, or organizations (e.g., "MIT", "Stanford University", "Harvard")

Return ONLY a valid JSON object with this exact structure:
{
  "keywords": ["keyword1", "keyword2"],
  "authors": ["Author Name"],
  "years": ["2020"],
  "institutions": ["Institution Name"]
}

Rules:
- If an entity is not found, use an empty array []
- For years, extract just the year number (e.g., "2020" not "in 2020")
- For year ranges, return both years separately (e.g., ["2020", "2023"] for "2020-2023")
- For relative years like "after 2020", return ["2020"] and note the operator separately if needed
- Normalize author names to proper case (e.g., "john smith" -> "John Smith")
- Only include institutions that are clearly academic/research institutions
- Keywords should be meaningful research terms, not common words like "papers" or "research"
"""

        user_prompt = f"Extract entities from this search query: {query}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=500,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        parsed = json.loads(content)
        
        # Ensure all required keys exist
        result = {
            "keywords": parsed.get("keywords", []),
            "authors": parsed.get("authors", []),
            "years": parsed.get("years", []),
            "institutions": parsed.get("institutions", [])
        }
        
        # Filter out empty strings and normalize
        result["keywords"] = [k.strip() for k in result["keywords"] if k and k.strip()]
        result["authors"] = [a.strip() for a in result["authors"] if a and a.strip()]
        result["years"] = [str(y).strip() for y in result["years"] if y and str(y).strip()]
        result["institutions"] = [i.strip() for i in result["institutions"] if i and i.strip()]
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing GPT response as JSON: {e}")
        if 'content' in locals():
            print(f"   Response was: {content}")
        return {"keywords": [], "authors": [], "years": [], "institutions": []}
    except Exception as e:
        print(f"⚠️ Error calling GPT API: {e}")
        import traceback
        traceback.print_exc()
        return {"keywords": [], "authors": [], "years": [], "institutions": []}

