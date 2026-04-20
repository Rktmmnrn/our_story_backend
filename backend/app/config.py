from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Storage
    MEDIA_ROOT: str = "/app/media"
    MAX_PHOTO_SIZE_MB: int = 20
    MAX_VIDEO_SIZE_MB: int = 500
    MAX_AUDIO_SIZE_MB: int = 50

    # Initial Admin
    FIRST_ADMIN_EMAIL: EmailStr
    FIRST_ADMIN_PASSWORD: str

    # App Config
    ENVIRONMENT: str = "production"
    CORS_ORIGINS: str = ""
    FRONTEND_BASE_URL: str = "https://localhost:5173"

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@notrehistoire.app"

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        env_file_encoding="utf-8"
    )

    @property
    def smtp_configured(self) -> bool:
        """return true si SMTP est correctemeent configuré."""
        return bool(self.SMTP_HOST and self.SMTP_USER and self.SMTP_PASSWORD)

settings = Settings()