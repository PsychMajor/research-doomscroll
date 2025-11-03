"""
Analytics Router

Handles card visibility tracking and user engagement metrics.
Provides insights into which papers users view and when they reach end of feed.

Optional feature for understanding user behavior and improving recommendations.
"""

from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

from ..dependencies import get_user_id

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class CardVisibilityEvent(BaseModel):
    """Model for card visibility tracking"""
    card_number: int = Field(..., description="Position of card in feed (1-indexed)", ge=1)
    paper_id: str = Field(..., description="OpenAlex paper ID")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="When card became visible")
    viewport_time: Optional[int] = Field(None, description="Time in milliseconds card was in viewport", ge=0)


class SecondToLastEvent(BaseModel):
    """Model for second-to-last card tracking"""
    card_number: int = Field(..., description="Position of card in feed", ge=1)
    paper_id: str = Field(..., description="OpenAlex paper ID")
    total_cards: int = Field(..., description="Total number of cards currently loaded", ge=1)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Event timestamp")


class AnalyticsResponse(BaseModel):
    """Standard analytics response"""
    status: str = "success"
    message: Optional[str] = None


@router.post("/card/visible", response_model=AnalyticsResponse)
async def log_card_visible(
    event: CardVisibilityEvent,
    user_id: Optional[int] = Depends(get_user_id)
):
    """
    Log when a paper card becomes visible in the viewport.
    
    This endpoint tracks user engagement by recording when papers
    are actually viewed (scrolled into view). Useful for:
    - Understanding which papers get attention
    - Calculating engagement rates
    - Improving recommendation algorithms
    - A/B testing different layouts
    
    Args:
        event: Card visibility event with paper ID and position
        user_id: Optional authenticated user ID
    
    Returns:
        Success response with acknowledgment
    
    Example Request:
        POST /api/analytics/card/visible
        {
            "card_number": 5,
            "paper_id": "W2123456789",
            "viewport_time": 3500
        }
    """
    user_label = f"User {user_id}" if user_id else "Anonymous"
    
    log_message = (
        f"👁️  Card #{event.card_number} visible | "
        f"Paper: {event.paper_id} | "
        f"{user_label}"
    )
    
    if event.viewport_time:
        log_message += f" | Viewed for {event.viewport_time}ms"
    
    print(log_message)
    
    # TODO: Store in analytics database table
    # Example schema:
    # - user_id (nullable)
    # - paper_id
    # - card_position
    # - viewport_time
    # - timestamp
    # - session_id
    
    return AnalyticsResponse(
        message=f"Card visibility logged for paper {event.paper_id}"
    )


@router.post("/card/second-to-last", response_model=AnalyticsResponse)
async def log_second_to_last(
    event: SecondToLastEvent,
    user_id: Optional[int] = Depends(get_user_id)
):
    """
    Log when user reaches the second-to-last card in feed.
    
    This is a key engagement metric indicating:
    - User has scrolled through most/all content
    - May need more papers loaded (infinite scroll trigger)
    - High engagement session
    - Potential for recommendation refresh
    
    Typically triggers frontend to fetch next page of results.
    
    Args:
        event: Second-to-last card event with position and total
        user_id: Optional authenticated user ID
    
    Returns:
        Success response
    
    Example Request:
        POST /api/analytics/card/second-to-last
        {
            "card_number": 19,
            "paper_id": "W2987654321",
            "total_cards": 20
        }
    """
    user_label = f"User {user_id}" if user_id else "Anonymous"
    
    log_message = (
        f"🔔 SECOND-TO-LAST CARD | "
        f"{user_label} viewing card #{event.card_number} | "
        f"Paper: {event.paper_id} | "
        f"{event.card_number} of {event.total_cards} cards loaded"
    )
    
    print(log_message)
    
    # TODO: Store in analytics database
    # This event is useful for:
    # - Understanding feed depth (how far users scroll)
    # - Triggering backend prefetch of next page
    # - Session engagement metrics
    
    return AnalyticsResponse(
        message="Second-to-last card event logged"
    )


@router.post("/card/interaction", response_model=AnalyticsResponse)
async def log_card_interaction(
    paper_id: str = Body(..., embed=True),
    interaction_type: str = Body(..., embed=True),
    card_number: int = Body(..., embed=True),
    user_id: Optional[int] = Depends(get_user_id)
):
    """
    Log user interactions with paper cards.
    
    Tracks various interaction types:
    - "expand" - User clicked to expand abstract/details
    - "collapse" - User collapsed expanded content
    - "click_link" - User clicked external paper link
    - "copy_citation" - User copied citation
    - "hover" - Mouse hover over card (desktop)
    
    Args:
        paper_id: OpenAlex paper ID
        interaction_type: Type of interaction
        card_number: Position in feed
        user_id: Optional authenticated user ID
    
    Returns:
        Success response
    
    Example Request:
        POST /api/analytics/card/interaction
        {
            "paper_id": "W2123456789",
            "interaction_type": "expand",
            "card_number": 3
        }
    """
    user_label = f"User {user_id}" if user_id else "Anonymous"
    
    print(
        f"🔗 Card Interaction | "
        f"Type: {interaction_type} | "
        f"Paper: {paper_id} | "
        f"Position: #{card_number} | "
        f"{user_label}"
    )
    
    # TODO: Store in analytics database
    # Useful for understanding:
    # - Which papers get clicked vs just viewed
    # - Abstract expansion rates
    # - External link click-through rates
    
    return AnalyticsResponse(
        message=f"Interaction '{interaction_type}' logged"
    )


@router.post("/session/start", response_model=AnalyticsResponse)
async def log_session_start(
    search_params: Dict = Body(...),
    user_id: Optional[int] = Depends(get_user_id)
):
    """
    Log the start of a new browsing session.
    
    Captures initial search parameters and user context when
    they begin browsing papers. Useful for:
    - Session-based analytics
    - Understanding search patterns
    - A/B testing different UX flows
    
    Args:
        search_params: Dictionary with topics, authors, sort_by, etc.
        user_id: Optional authenticated user ID
    
    Returns:
        Success response with session acknowledgment
    
    Example Request:
        POST /api/analytics/session/start
        {
            "topics": ["machine learning", "neural networks"],
            "authors": ["Andrew Ng"],
            "sort_by": "recency"
        }
    """
    user_label = f"User {user_id}" if user_id else "Anonymous"
    
    topics = search_params.get('topics', [])
    authors = search_params.get('authors', [])
    sort_by = search_params.get('sort_by', 'recency')
    
    print(
        f"🚀 Session Start | "
        f"{user_label} | "
        f"Topics: {topics} | "
        f"Authors: {authors} | "
        f"Sort: {sort_by}"
    )
    
    # TODO: Generate session ID and store in database
    # Return session_id to frontend for subsequent events
    
    return AnalyticsResponse(
        message="Session started"
    )


@router.get("/stats/summary")
async def get_analytics_summary(user_id: int = Depends(get_user_id)):
    """
    Get analytics summary for current user (authenticated only).
    
    Provides insights into user's engagement:
    - Total papers viewed
    - Average viewport time
    - Most viewed topics/authors
    - Session statistics
    
    Requires authentication.
    
    Returns:
        Analytics summary object
    
    Example Response:
        {
            "total_cards_viewed": 1250,
            "total_sessions": 45,
            "avg_cards_per_session": 27.8,
            "avg_viewport_time_ms": 4200,
            "top_topics": ["machine learning", "neural networks"],
            "top_authors": ["Andrew Ng", "Geoffrey Hinton"]
        }
    """
    # TODO: Query analytics database for user statistics
    
    # Placeholder response
    return {
        "total_cards_viewed": 0,
        "total_sessions": 0,
        "avg_cards_per_session": 0,
        "avg_viewport_time_ms": 0,
        "top_topics": [],
        "top_authors": [],
        "message": "Analytics storage not yet implemented"
    }
