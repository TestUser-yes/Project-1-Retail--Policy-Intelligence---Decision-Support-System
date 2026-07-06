"""Initialize database schema from SQLAlchemy models and load PDF documents."""

import os
import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from app.database.session import engine
from app.models.base import Base

if __name__ == "__main__":
    print("[INFO] Step 1: Creating database tables from models...")

    try:
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database tables created!")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        sys.exit(1)

    print("")
    print("[INFO] Step 2: Loading PDF documents from Documents/ folder...")

    try:
        from app.rag.ingest import ingest_documents
        ingest_documents()
        print("[SUCCESS] PDF documents loaded and indexed!")
    except Exception as e:
        print(f"[WARNING] Could not load PDFs: {e}")
        print("[INFO] You can load PDFs later by running: python -c \"from app.rag.ingest import ingest_documents; ingest_documents()\"")

    print("")
    print("[SUCCESS] Database initialization complete!")
    sys.exit(0)
