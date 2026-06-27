from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"


def load_environment() -> None:
    """Load local environment variables from the project .env file."""
    load_dotenv(PROJECT_ROOT / ".env")

