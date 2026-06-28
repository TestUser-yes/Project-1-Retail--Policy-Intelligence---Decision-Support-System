from __future__ import annotations

import sqlite3
from pathlib import Path

from .base import Base
from .session import SessionLocal, engine, get_db


DB_PATH = Path(__file__).resolve().parents[2] / "database" / "database" / "retail_policy.db"


def get_db_connection() -> sqlite3.Connection:
    """Open a SQLite connection to the project database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
