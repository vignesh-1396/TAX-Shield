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
    # In production, this should be a stable secret key
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "temporary_secret_key_for_development_only_replace_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # DATABASE
    # If DATABASE_URL is not set, it defaults to SQLite
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # GSP Configuration
    # Modes: "mock" (default), "sandbox" (zoop.one)
    GSP_MODE: str = os.getenv("GSP_MODE", "mock")
    SANDBOX_CLIENT_ID: Optional[str] = os.getenv("SANDBOX_CLIENT_ID")
    SANDBOX_SECRET: Optional[str] = os.getenv("SANDBOX_SECRET")

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

    class Config:
        case_sensitive = True

settings = Settings()
