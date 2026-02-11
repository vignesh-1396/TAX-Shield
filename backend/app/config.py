from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # Database Configuration
    database_url: str
    
    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    
    # GSP Configuration
    gsp_mode: str = "sandbox"
    sandbox_client_id: str
    sandbox_secret: str
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
