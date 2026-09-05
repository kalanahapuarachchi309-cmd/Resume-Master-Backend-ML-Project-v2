"""Application Configuration Module."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume Master AI"
    API_V1_STR: str = "/api"

settings = Settings()
