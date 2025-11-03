"""
Configuration management for the application
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "Research Doomscroll"
    debug: bool = False
    
    # Security
    secret_key: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-use-python-secrets")
    
    # OAuth
    google_client_id: str = os.environ.get("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    
    # Database
    database_url: str = os.environ.get("DATABASE_URL", "")
    
    # OpenAlex API
    openalex_email: str = os.environ.get("OPENALEX_EMAIL", "samayshah@gmail.com")
    
    # NLTK
    nltk_data_path: str = os.environ.get("NLTK_DATA", "/tmp/nltk_data")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
