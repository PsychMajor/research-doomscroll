"""
Proxy API Router

Endpoints for proxying external content to bypass X-Frame-Options restrictions.
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from typing import Optional
import httpx
from urllib.parse import urljoin, urlparse
import re

router = APIRouter(prefix="/api/proxy", tags=["proxy"])


@router.get("/content", response_class=HTMLResponse)
async def proxy_content(
    url: str = Query(..., description="URL to proxy"),
    timeout: int = Query(30, ge=5, le=60, description="Request timeout in seconds")
):
    """
    Proxy external content to bypass X-Frame-Options restrictions.
    
    Fetches HTML content from the provided URL, strips security headers,
    and rewrites relative URLs to absolute URLs so resources load correctly.
    
    **Query Parameters:**
    - `url`: The URL to proxy (must be a valid HTTP/HTTPS URL)
    - `timeout`: Request timeout in seconds (default: 30, max: 60)
    
    **Returns:**
    HTML content with modified headers and URLs
    
    **Example:**
    ```
    GET /api/proxy/content?url=https://www.pnas.org/doi/10.1073/pnas.1234567890
    ```
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or parsed.scheme not in ['http', 'https']:
            raise HTTPException(
                status_code=400,
                detail="Invalid URL scheme. Only http and https are allowed."
            )
        
        # Fetch content with comprehensive browser headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': parsed.scheme + '://' + parsed.netloc + '/',
        }
        
        # Create client with cookies enabled and better redirect handling
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            cookies={},
            verify=True
        ) as client:
            # Try GET request first
            try:
                response = await client.get(url, headers=headers)
            except httpx.HTTPStatusError as e:
                # If 403, try with different approach - some sites check for specific patterns
                if e.response.status_code == 403:
                    # Try without some security headers that might trigger bot detection
                    simpler_headers = {
                        'User-Agent': headers['User-Agent'],
                        'Accept': headers['Accept'],
                        'Accept-Language': headers['Accept-Language'],
                        'Referer': headers['Referer'],
                    }
                    response = await client.get(url, headers=simpler_headers)
                else:
                    raise
            
            response.raise_for_status()
            
            content = response.text
            content_type = response.headers.get('content-type', 'text/html')
            
            # Only process HTML content
            if 'text/html' not in content_type:
                raise HTTPException(
                    status_code=400,
                    detail="URL does not return HTML content"
                )
            
            # Rewrite relative URLs to absolute URLs
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Fix relative links (href, src, srcset, etc.)
            content = re.sub(
                r'(href|src|srcset|action|formaction)=["\']([^"\']+)["\']',
                lambda m: f'{m.group(1)}="{urljoin(base_url, m.group(2))}"',
                content
            )
            
            # Fix relative URLs in CSS (url(...))
            content = re.sub(
                r'url\(["\']?([^"\'()]+)["\']?\)',
                lambda m: f'url("{urljoin(base_url, m.group(1))}")',
                content
            )
            
            # Remove X-Frame-Options and CSP meta tags from HTML
            content = re.sub(
                r'<meta[^>]*http-equiv=["\']X-Frame-Options["\'][^>]*>',
                '',
                content,
                flags=re.IGNORECASE
            )
            content = re.sub(
                r'<meta[^>]*http-equiv=["\']Content-Security-Policy["\'][^>]*>',
                '',
                content,
                flags=re.IGNORECASE
            )
            
            # Return HTML with headers that allow embedding
            return HTMLResponse(
                content=content,
                headers={
                    'X-Frame-Options': 'ALLOWALL',
                    'Content-Security-Policy': "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;",
                    'X-Content-Type-Options': 'nosniff',
                }
            )
            
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 403:
            # 403 Forbidden - site is blocking the proxy request
            raise HTTPException(
                status_code=403,
                detail="The publisher's website is blocking proxy requests. This is common for academic publishers that use advanced bot detection. Please use 'Open in New Tab' instead."
            )
        elif status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="The requested page was not found."
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=f"Failed to fetch URL: HTTP {status_code}"
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request timeout. The server took too long to respond."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to URL: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error proxying content: {str(e)}"
        )

