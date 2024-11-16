from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List, Optional
from functools import lru_cache
import os

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    PROJECT_NAME: str = 'Cover'
    DEBUG: bool = True
    
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ALLOWED_ORIGINS: List[str] = [
        "capacitor://localhost",
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0"
    ]
    
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        

settings = Settings()

# Use the existing instance
@lru_cache()
def get_settings() -> Settings:
    return settings 