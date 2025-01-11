from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn
import os
import dotenv

dotenv.load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Advanced API"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # FastAPI backend
        "http://localhost",
    ]
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-123")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    SERVER_NAME: str = "localhost"
    
    # Database
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "Abhi123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "dbms")
    POSTGRES_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # Database Pool Settings
    DB_POOL_SIZE: int = os.getenv("DB_POOL_SIZE", 5)
    DB_MAX_OVERFLOW: int = os.getenv("DB_MAX_OVERFLOW", 10)
    DB_ECHO: bool = os.getenv("DB_ECHO", True)
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    
    # Debug mode
    DEBUG: bool = bool(os.getenv("DEBUG", False))
    
    # Version and description
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI Advanced API"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()