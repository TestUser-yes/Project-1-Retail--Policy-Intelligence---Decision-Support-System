"""
Application configuration.

Loads all environment variables from the .env file
using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    DATABASE_URL: str  # OPTIONAL now (not required anymore)

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
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
