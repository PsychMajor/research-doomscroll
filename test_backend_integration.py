#!/usr/bin/env python3
"""
Integration test script for the new modular backend.

Tests all API endpoints to ensure they work correctly.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

async def test_endpoint(client: httpx.AsyncClient, method: str, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test a single endpoint and return result"""
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{path}")
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{path}", json=data or {})
        elif method == "PUT":
            response = await client.put(f"{BASE_URL}{path}", json=data or {})
        elif method == "DELETE":
            response = await client.delete(f"{BASE_URL}{path}")
        else:
            return {"status": "error", "message": f"Unknown method: {method}"}
        
        return {
            "status": "success" if response.status_code < 400 else "error",
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    """Run all integration tests"""
    print("🧪 Backend Integration Tests")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tests = [
            # Basic endpoints
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/docs", "OpenAPI docs"),
            
            # Auth endpoints (without actual OAuth flow)
            ("GET", "/api/auth/status", "Auth status"),
            ("GET", "/api/auth/me", "Current user info"),
            
            # Papers endpoints (will need OpenAlex API)
            ("GET", "/api/papers/search?topics=machine+learning&page=1", "Search papers"),
            
            # Profile endpoints (anonymous user)
            ("GET", "/api/profile", "Get profile (anonymous)"),
            
            # Feedback endpoints
            ("GET", "/api/feedback", "Get feedback"),
            
            # Folders endpoints
            ("GET", "/api/folders", "List folders"),
            
            # Analytics endpoints
            ("POST", "/api/analytics/card/visible", "Log card visibility", {
                "card_number": 1,
                "paper_id": "W2123456789"
            }),
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            method, path, description = test[:3]
            data = test[3] if len(test) > 3 else None
            
            print(f"\n📍 Testing: {description}")
            print(f"   {method} {path}")
            
            result = await test_endpoint(client, method, path, data)
            
            if result["status"] == "success":
                print(f"   ✅ Status: {result['status_code']}")
                passed += 1
            else:
                print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
                if "status_code" in result:
                    print(f"      Status: {result['status_code']}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("✅ All tests passed!")
        else:
            print(f"⚠️  {failed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())
