"""
Application configuration.

Loads all environment variables from the .env file
using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # -------------------------
    # Project
    # -------------------------
    PROJECT_NAME: str = "Retail Policy Intelligence & Decision Support System"
    API_VERSION: str = "1.0.0"

    # -------------------------
    # Database
    # -------------------------
    DATABASE_URL: str = "sqlite:///./policy_system.db"  # Local SQLite database

    # -------------------------
    # OpenAI
    # -------------------------
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # Ollama config
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "phi3:mini"

    # -------------------------
    # Langfuse
    # -------------------------
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"

    # -------------------------
    # SLO Enforcement
    # -------------------------
    SLO_ENFORCE_LATENCY: bool = True
    SLO_ENFORCE_CONFIDENCE: bool = True
    SLO_ENFORCE_ACCURACY: bool = True
    SLO_LATENCY_TARGET_MS: int = 2000
    SLO_LATENCY_HARD_LIMIT_MS: int = 2400
    SLO_CONFIDENCE_MIN: float = 0.70

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
