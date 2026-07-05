"""Create the policy_documents table with pgvector support."""

import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from app.database.session import engine

if __name__ == "__main__":
    print("[INFO] Creating policy_documents table with pgvector...")

    sql = """
    CREATE TABLE IF NOT EXISTS policy_documents (
        id VARCHAR(36) PRIMARY KEY,
        title VARCHAR(500) NOT NULL,
        content TEXT NOT NULL,
        category VARCHAR(100),
        embedding vector(1536),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_policy_embedding ON policy_documents
    USING ivfflat (embedding vector_cosine_ops);
    """

    try:
        with engine.connect() as conn:
            # Create extension first
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("[OK] pgvector extension enabled")

            # Create table
            for stmt in sql.split(";"):
                if stmt.strip():
                    conn.execute(text(stmt))
            conn.commit()
            print("[SUCCESS] policy_documents table created with pgvector support!")

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
