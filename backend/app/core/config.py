"""Application Configuration Module (Kalana)."""
import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    PROJECT_NAME: str = "Resume Master AI Screening & Job Matching"
    API_V1_STR: str = "/api"
    DEBUG: bool = True

    # Database Settings (Defaults to local SQLite if PostgreSQL is not configured)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./resume_matcher.db"
    )

    # Security & JWT Settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS Settings
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"

    # Cloudinary Cloud Storage Settings (Mahen & Team)
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME") or "djsdwv2na"
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY") or "216632618736747"
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET") or "Bnfp7Px9C57hfxcXrdo2xYx26LY"
    CLOUDINARY_FOLDER: str = os.getenv("CLOUDINARY_FOLDER") or "resume_master"

    @property
    def cors_origins(self) -> List[str]:
        """Convert comma-separated origins string to a clean list."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
