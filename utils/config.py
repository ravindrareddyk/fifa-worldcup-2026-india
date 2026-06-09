"""
Centralized Configuration (Professional Best Practice).
Uses pydantic-settings for type-safe .env / environment variable loading.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class AppConfig(BaseSettings):
    """Application configuration with sensible defaults for demo/portfolio use."""

    # Environment
    env: str = Field(default="development", validation_alias="ENV")
    debug: bool = Field(default=True, validation_alias="DEBUG")

    # Live Scores API (optional - for real integration)
    football_api_key: str | None = Field(default=None, validation_alias="FOOTBALL_API_KEY")

    # Monetization / Contest settings
    max_leaderboard_entries: int = 10
    points_base: int = 50
    points_ml_bonus: int = 30

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Streamlit / Deployment
    streamlit_server_port: int = 8501

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore unknown env vars


# Singleton config instance
config = AppConfig()

# Convenience for modules that don't want to import the whole thing
def get_config() -> AppConfig:
    return config


# Example usage in other modules:
# from utils.config import config
# if config.football_api_key: ...