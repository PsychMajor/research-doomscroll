"""
Pydantic models for Paper entities
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Author(BaseModel):
    """Author information"""
    name: str
    id: Optional[str] = None


class Paper(BaseModel):
    """Research paper model"""
    paper_id: str = Field(..., alias="paperId")
    title: str
    abstract: Optional[str] = None
    authors: List[Author] = []
    year: Optional[int] = None
    venue: Optional[str] = None
    citation_count: int = Field(0, alias="citationCount")
    url: Optional[str] = None
    tldr: Optional[str] = None
    source: str = "openalex"
    doi: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Allow both paperId and paper_id


class PaperSearchParams(BaseModel):
    """Parameters for searching papers"""
    topics: Optional[str] = None
    authors: Optional[str] = None
    sort_by: str = "recency"
    page: int = Field(1, ge=1)
    per_page: int = Field(200, ge=1, le=200)
