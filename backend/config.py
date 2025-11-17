"""
Configuration management for the application
"""
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",  # .env in project root
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App settings
    app_name: str = "Research Doomscroll"
    debug: bool = False
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production-use-python-secrets"
    
    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Database
    database_url: str = ""
    
    # Firebase
    firebase_project_id: str = ""
    firebase_credentials_path: str = ""  # Path to service account JSON file
    use_firebase: bool = False  # Feature flag to enable Firebase
    
    # OpenAlex API
    openalex_email: str = "samayshah@gmail.com"
    
    # OpenAI API
    openai_api_key: str = ""
    
    # NLTK
    nltk_data_path: str = "/tmp/nltk_data"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
