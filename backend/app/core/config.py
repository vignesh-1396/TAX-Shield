import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
from pydantic import AnyHttpUrl
from pydantic_core import MultiHostUrl
from typing import List, Optional, Union
from pydantic import BaseModel, validator

class Settings(BaseModel):
    PROJECT_NAME: str = "ITC Shield"
    API_V1_STR: str = "/api/v1"
    
    # Base directory
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BATCH_OUTPUT_DIR: str = os.path.join(BASE_DIR, "output", "batches")
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # DATABASE
    # If DATABASE_URL is not set, it defaults to SQLite
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Database Connection Pool Settings
    DB_POOL_MIN_CONN: int = int(os.getenv("DB_POOL_MIN_CONN", "5"))
    DB_POOL_MAX_CONN: int = int(os.getenv("DB_POOL_MAX_CONN", "50"))
    DB_CONNECT_TIMEOUT: int = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
    DB_STATEMENT_TIMEOUT: int = int(os.getenv("DB_STATEMENT_TIMEOUT", "30000"))  # 30 seconds
    
    # GSP Configuration
    # Modes: "mock" (default), "sandbox" (zoop.one)
    GSP_MODE: str = os.getenv("GSP_MODE", "mock")
    SANDBOX_CLIENT_ID: Optional[str] = os.getenv("SANDBOX_CLIENT_ID")
    SANDBOX_SECRET: Optional[str] = os.getenv("SANDBOX_SECRET")
    
    # Redis Cache Configuration
    # Redis Cache Configuration
    # Defaults to None if not set or invalid
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """Validate JWT secret key - CRITICAL SECURITY CHECK"""
        if not v:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required! "
                "Set a strong secret key in your .env file."
            )
        
        # Check for dangerous default values
        dangerous_defaults = [
            "temporary_secret_key_for_development_only_replace_in_production",
            "secret",
            "changeme",
            "password",
            "default"
        ]
        
        if v.lower() in dangerous_defaults:
            raise ValueError(
                f"JWT_SECRET_KEY cannot be '{v}'. "
                "Use a strong, random secret key. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        # Warn if secret is too short
        if len(v) < 32:
            import warnings
            warnings.warn(
                f"JWT_SECRET_KEY is only {len(v)} characters. "
                "Recommended: 32+ characters for production security."
            )
        
        return v

    class Config:
        case_sensitive = True

settings = Settings()
