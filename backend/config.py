import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "NammaSevai AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database Settings (Default SQLite for standalone resilience; supports Postgres via DATABASE_URL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./nammasevai.db"
    )
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Security & Admin Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nammasevai-super-secret-key-tamil-nadu-2026")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "nammasevai-admin-secret-2026")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
