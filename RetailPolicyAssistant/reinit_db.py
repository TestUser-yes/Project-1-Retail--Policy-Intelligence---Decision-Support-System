"""Reinitialize database schema with pgvector support."""

import os
from dotenv import load_dotenv

load_dotenv()

# Import ALL models to register them with Base
from app.models.base import Base
from app.models.models import PolicyDocument, User, QueryLog
from app.models.ai_queries import AIQuery
from app.models.audit import AuditLog
from app.models.evaluation import EvaluationRun, EvaluationResult
from app.database.session import engine

if __name__ == "__main__":
    print("[INFO] Creating all tables with pgvector support...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database initialized with pgvector support!")
        print("[INFO] PolicyDocument.embedding is now Vector(1536) type")
        print("\n[INFO] Created tables:")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        for table in sorted(inspector.get_table_names()):
            print(f"  - {table}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
