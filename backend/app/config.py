from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # Database Configuration
    database_url: str
    
    # Auth
    jwt_secret: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    
    # GSP Configuration
    gsp_mode: str = "sandbox"
    sandbox_client_id: str = Field(..., alias="SANDBOX_CLIENT_ID")
    sandbox_secret: str = Field(..., alias="SANDBOX_SECRET")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env
        populate_by_name = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
