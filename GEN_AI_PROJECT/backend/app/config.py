"""Configuration management for the backend application."""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Required
    gemini_api_key: str
    
    # Optional with defaults
    github_token: Optional[str] = None
    max_files: int = 200
    max_file_size_kb: int = 100
    max_total_chars: int = 200000  # ~200k chars for Gemini
    clone_timeout: int = 60
    allowed_branches: Optional[str] = None  # Comma-separated list
    
    # Server settings
    backend_port: int = 8000
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_settings():
    """Validate settings on startup."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required. Set it in .env file or environment variable.")
    
    if settings.max_files < 1:
        raise ValueError("MAX_FILES must be at least 1")
    
    if settings.max_file_size_kb < 1:
        raise ValueError("MAX_FILE_SIZE_KB must be at least 1")
    
    return True
