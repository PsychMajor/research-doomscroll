"""
Pydantic models for User entities
"""
from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    """User model"""
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = Field(None, alias="picture_url")
    
    class Config:
        populate_by_name = True


class UserProfile(BaseModel):
    """User profile with preferences"""
    topics: list[str] = []
    authors: list[str] = []
    folders: list[dict] = []
    
    class Config:
        from_attributes = True
