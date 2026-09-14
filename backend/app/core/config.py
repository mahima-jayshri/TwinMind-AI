from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: Optional[str] = "demo-google-client-id"
    GOOGLE_CLIENT_SECRET: Optional[str] = "demo-google-client-secret"
    GEMINI_API_KEY: Optional[str] = ""
    SECRET_KEY: str = "twinmind_development_secret_key_change_in_production"
    DATABASE_URL: str = "sqlite+aiosqlite:///./twinmind.db"
    FRONTEND_URL: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

