"""Verify database tables were created."""

import os
from dotenv import load_dotenv
from sqlalchemy import text, inspect

load_dotenv()

from app.database.session import engine

if __name__ == "__main__":
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"[INFO] Found {len(tables)} tables in Neon PostgreSQL:\n")
        for table in sorted(tables):
            print(f"  - {table}")

        if tables:
            print("\n[SUCCESS] Database is ready!")
        else:
            print("\n[WARN] No tables found - initialization may have failed")

    except Exception as e:
        print(f"[ERROR] Failed to verify database: {e}")
