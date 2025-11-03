"""
Pydantic models for Feedback entities
"""
from pydantic import BaseModel
from typing import Literal


class FeedbackAction(BaseModel):
    """Model for paper feedback actions"""
    paper_id: str
    action: Literal["liked", "disliked"]


class FeedbackResponse(BaseModel):
    """Response model for feedback queries"""
    liked: list[str] = []
    disliked: list[str] = []
