import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
