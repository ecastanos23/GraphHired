"""
Application Configuration
Environment variables and settings management
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database - SQLite for local dev, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./graphhired.db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "graphhired"
    USE_SQLITE: bool = True
    
    def get_database_url(self) -> str:
        if self.USE_SQLITE:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    

    # Gemini (Google AI Studio)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Application
    DEBUG: bool = True
    BACKEND_PORT: int = 8000
    PROJECT_NAME: str = "GraphHired API"
    
    class Config:
        env_file = (
            str(ROOT_DIR / ".env"),
            str(BACKEND_DIR / ".env"),
            ".env",
        )
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
