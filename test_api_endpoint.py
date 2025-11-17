#!/usr/bin/env python3
"""
Test script for the search query API endpoint

Tests the /api/papers/search/query endpoint to verify:
1. Query parsing (keywords and authors extraction)
2. API response format
3. Error handling
"""

import requests
import json
import sys
from typing import Dict, List

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_parser_directly(query: str):
    """Test the parser directly without making API calls"""
    print(f"\n{'='*60}")
    print(f"Testing parser directly for: '{query}'")
    print(f"{'='*60}")
    
    try:
        sys.path.insert(0, 'backend')
        from utils.ai_query_parser import parse_search_query
        
        result = parse_search_query(query)
        print(f"✅ Parsed successfully!")
        print(f"   Keywords: {result.get('keywords', [])}")
        print(f"   Authors: {result.get('authors', [])}")
        print(f"   Years: {result.get('years', [])}")
        print(f"   Institutions: {result.get('institutions', [])}")
        return result
    except Exception as e:
        print(f"❌ Parser error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_api_endpoint(query: str, sort_by: str = "recency", page: int = 1, per_page: int = 5, show_details: bool = True):
    """Test the API endpoint with a query"""
    print(f"\n{'='*60}")
    print(f"Testing API endpoint for: '{query}'")
    print(f"{'='*60}")
    
    # First, show what the parser will extract
    parser_result = test_parser_directly(query)
    if not parser_result:
        print("⚠️  Parser failed, skipping API test")
        return None
    
    url = f"{BASE_URL}/api/papers/search/query"
    params = {
        "q": query,
        "sort_by": sort_by,
        "page": page,
        "per_page": per_page
    }
    
    try:
        print(f"\n📡 Making API request...")
        print(f"   URL: {url}")
        print(f"   Query: {query}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Received {len(data)} papers")
            
            if show_details and data:
                print(f"\n📄 First paper details:")
                first_paper = data[0]
                print(f"   Title: {first_paper.get('title', 'N/A')}")
                authors = first_paper.get('authors', [])
                if authors:
                    author_names = [a.get('name', '') for a in authors[:3]]
                    print(f"   Authors: {', '.join(author_names)}")
                    if len(authors) > 3:
                        print(f"   ... and {len(authors) - 3} more")
                else:
                    print(f"   Authors: (none)")
                print(f"   Year: {first_paper.get('publicationYear', 'N/A')}")
                print(f"   Citations: {first_paper.get('citationCount', 0)}")
                print(f"   Venue: {first_paper.get('venue', 'N/A')}")
                if first_paper.get('abstract'):
                    abstract_preview = first_paper.get('abstract', '')[:100]
                    print(f"   Abstract: {abstract_preview}...")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detail: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {BASE_URL}")
        print(f"   Make sure the backend server is running!")
        return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run test cases"""
    print("🧪 Testing Search Query API Endpoint")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        # (query, description)
        ("machine learning by John Smith", "Keywords + author with 'by'"),
        ("pain research by theodore price", "Keywords + author with 'by'"),
        ("quantum computing papers", "Keywords only"),
        ("John Smith, Jane Doe neural networks", "Authors first, then keywords"),
        ("machine learning, deep learning by John Smith and Jane Doe", "Multiple keywords and authors"),
        ("from Michael J. Iadarola pain research", "Author with 'from', then keywords"),
        ("spinal cord injury by Matthew R. Sapio", "Multi-word keywords + author"),
        ("GPCR research", "Acronym keywords"),
        # Year tests
        ("machine learning in 2020", "Keywords + single year"),
        ("quantum computing 2020-2023", "Keywords + year range"),
        ("neural networks after 2020", "Keywords + after year"),
        ("deep learning before 2023", "Keywords + before year"),
        ("AI research since 2020", "Keywords + since year"),
        ("robotics until 2023", "Keywords + until year"),
        # Institution tests
        ("machine learning at MIT", "Keywords + institution"),
        ("quantum computing from Harvard University", "Keywords + institution with 'from'"),
        ("neural networks at Stanford University", "Keywords + institution"),
        # Combined tests
        ("pain research by John Smith in 2020", "Keywords + author + year"),
        ("machine learning at MIT after 2020", "Keywords + institution + year"),
        ("quantum computing by Jane Doe at Stanford University in 2022", "Keywords + author + institution + year"),
    ]
    
    print("\n" + "="*60)
    print("PHASE 1: Testing Parser Directly")
    print("="*60)
    
    parser_results = []
    for query, description in test_cases:
        print(f"\n📝 Test: {description}")
        result = test_parser_directly(query)
        if result:
            parser_results.append((query, result))
    
    print("\n" + "="*60)
    print("PHASE 2: Testing API Endpoint")
    print("="*60)
    print("\n⚠️  Note: This requires the backend server to be running on http://localhost:8000")
    print("   The API endpoint requires session cookies, so it may fail if not authenticated.")
    print("   However, the parser tests above should work regardless.\n")
    
    # Test a few queries via API
    api_test_cases = [
        ("pain research by theodore price", "Real-world example (lowercase author)"),
        ("machine learning by John Smith", "Simple query (capitalized author)"),
        ("quantum computing", "Keywords only"),
        ("spinal cord injury by Matthew R. Sapio", "Multi-word keywords + middle initial"),
        ("machine learning in 2020", "Keywords + year"),
        ("quantum computing after 2020", "Keywords + after year"),
        ("neural networks at MIT", "Keywords + institution"),
        ("pain research by John Smith in 2020", "Keywords + author + year"),
    ]
    
    api_results = []
    for query, description in api_test_cases:
        print(f"\n📝 API Test: {description}")
        result = test_api_endpoint(query, per_page=3, show_details=True)
        if result:
            api_results.append((query, len(result)))
        print()  # Add spacing between tests
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\n✅ Parser tests completed: {len(parser_results)}/{len(test_cases)}")
    print(f"✅ API tests completed: {len(api_results)}/{len(api_test_cases)}")
    
    if parser_results:
        print("\n📊 Parser Results Summary:")
        for query, result in parser_results:
            keywords = result.get('keywords', [])
            authors = result.get('authors', [])
            years = result.get('years', [])
            institutions = result.get('institutions', [])
            print(f"   '{query}'")
            print(f"      → Keywords: {keywords if keywords else '(none)'}")
            print(f"      → Authors: {authors if authors else '(none)'}")
            print(f"      → Years: {years if years else '(none)'}")
            print(f"      → Institutions: {institutions if institutions else '(none)'}")

if __name__ == "__main__":
    main()

