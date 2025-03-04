from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    PROJECT_NAME: str = 'Cover'
    DEBUG: bool = True
    
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    PORT: int = 8000
    
    ALLOWED_ORIGINS: List[str] = [
        "capacitor://localhost",
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0"
    ]
    
    PSQL_URL: str
    DATABASE_URL: str
    SUPABASE_KEY: str
    TWILIO_ASID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_SERVICE_ID: str

    OPENAI_API_KEY: str
    
    ENVIRONMENT: str
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()

@lru_cache()
def get_settings() -> Settings:
    return settings
