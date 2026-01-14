from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "EOG Practice Test Generator"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development" # "development", "production", "testing"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # Security
    # In production, this MUST be set via environment variable
    SECRET_KEY: str = "development-secret-key-32-chars-at-least!!!" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    # List of allowed origins, e.g., ["http://localhost:5173", "https://app.eduapp.com"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "development"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignore extra env vars
    )

settings = Settings()
