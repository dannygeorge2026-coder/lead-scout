from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    DATABASE_URL: str = "checkpoints.sqlite"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"

    # Default Gemini model settings
    DEFAULT_MODEL: str = "gemini-3.5-flash-lite"
    MODEL_TEMPERATURE: float = 0.2

    model_config = SettingsConfigDict(
    env_file="backend/.env",
    env_file_encoding="utf-8",
    extra="ignore"
    )


settings = Settings()