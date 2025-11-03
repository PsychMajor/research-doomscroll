"""
Pydantic models for Folder entities
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class FolderBase(BaseModel):
    """Base folder model"""
    name: str


class FolderCreate(FolderBase):
    """Model for creating a folder"""
    pass


class FolderUpdate(BaseModel):
    """Model for updating a folder"""
    name: Optional[str] = None


class Folder(FolderBase):
    """Complete folder model with papers"""
    id: str
    papers: List[dict] = []  # List of paper objects
    
    class Config:
        from_attributes = True


class AddPaperToFolder(BaseModel):
    """Model for adding a paper to a folder"""
    folder_id: str
    paper_id: str
    paper_data: Optional[dict] = None  # Optional full paper data
