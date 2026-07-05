"""Initialize database schema from SQLAlchemy models."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app.database.session import engine
from app.models.base import Base

if __name__ == "__main__":
    print("[INFO] Creating database tables from models...")

    try:
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database initialized successfully!")
        print("[INFO] All tables created in Neon PostgreSQL")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        sys.exit(1)
