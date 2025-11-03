"""
API Routers

Domain-specific API endpoints organized by resource type.
"""

from . import papers, profile, feedback, folders, auth, analytics

__all__ = ["papers", "profile", "feedback", "folders", "auth", "analytics"]
