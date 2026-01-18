"""
Configuration management for the blog generator application.
Loads environment variables and provides application settings.
"""

from pydantic_settings import BaseSettings
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini Configuration
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    
    # Application Settings
    app_env: str = "development"
    log_level: str = "INFO"
    max_content_length: int = 10000
    request_timeout: int = 30
    
    # Model Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    use_faiss_cache: bool = False
    
    # Unsplash API (for images)
    unsplash_access_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()


def setup_logging():
    """Configure application logging."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


# Initialize settings
settings = get_settings()
setup_logging()
