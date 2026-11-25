import os
import json
import logging
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union

class Settings(BaseSettings):
    APP_NAME: str = "BharatSevai AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database Settings (Default SQLite for standalone resilience; supports Postgres via DATABASE_URL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./nammasevai.db"
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS (supports comma-separated string, JSON list, or python list)
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return ["*"]
    
    # Security & Admin Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nammasevai-super-secret-key-tamil-nadu-2026")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "nammasevai-admin-secret-2026")
    
    # Rate Limiting & Protection
    RATE_LIMIT_GENERAL_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_GENERAL_PER_MINUTE", "120"))
    RATE_LIMIT_MATCH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_MATCH_PER_MINUTE", "60"))
    RATE_LIMIT_ADMIN_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_ADMIN_PER_MINUTE", "40"))
    MAX_REQUEST_BODY_BYTES: int = int(os.getenv("MAX_REQUEST_BODY_BYTES", "5242880"))
    
    # AI Providers Configuration (Strict Priority Order: OpenAI -> Grok -> Gemini -> Deterministic Rule Engine)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")
    XAI_MODEL: str = os.getenv("XAI_MODEL", "grok-beta")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    AI_PROVIDER_TIMEOUT_SECONDS: int = int(os.getenv("AI_PROVIDER_TIMEOUT_SECONDS", "8"))
    AI_CIRCUIT_BREAKER_COOLDOWN_SECONDS: int = int(os.getenv("AI_CIRCUIT_BREAKER_COOLDOWN_SECONDS", "60"))
    AI_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(os.getenv("AI_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
    
    def check_production_security(self):
        """Audits security configuration upon startup."""
        logger = logging.getLogger("nammasevai.security")
        if self.APP_ENV == "production":
            if self.ADMIN_API_KEY in ("nammasevai-admin-secret-2026", "generate-a-secure-admin-key", "default"):
                logger.critical(
                    "CRITICAL SECURITY AUDIT: Production environment detected with default ADMIN_API_KEY! "
                    "You MUST set a strong random ADMIN_API_KEY in production environment variables."
                )
            if self.SECRET_KEY in ("nammasevai-super-secret-key-tamil-nadu-2026", "generate-a-secure-random-key-for-production"):
                logger.critical(
                    "CRITICAL SECURITY AUDIT: Production environment detected with default SECRET_KEY! "
                    "You MUST set a unique cryptographic SECRET_KEY in production."
                )
            if "*" in self.CORS_ORIGINS:
                logger.warning(
                    "SECURITY AUDIT: Production environment running with wildcard CORS ('*'). "
                    "Restrict CORS_ORIGINS to authorized government portal domains."
                )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
