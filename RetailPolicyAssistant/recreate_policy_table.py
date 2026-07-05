"""Recreate policy_documents table with correct schema for PDF indexing."""

import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from app.database.session import engine

if __name__ == "__main__":
    print("[INFO] Recreating policy_documents table with full schema...")

    try:
        with engine.connect() as conn:
            # Drop existing table
            print("[INFO] Dropping existing policy_documents table...")
            conn.execute(text("DROP TABLE IF EXISTS policy_documents CASCADE"))
            conn.commit()
            print("[OK] Table dropped")

            # Create new table with correct schema
            print("[INFO] Creating new policy_documents table...")
            sql = """
            CREATE TABLE policy_documents (
                id SERIAL PRIMARY KEY,
                document_name VARCHAR(500) NOT NULL,
                page_number INTEGER NOT NULL,
                chunk_number INTEGER NOT NULL,
                section VARCHAR(500),
                content TEXT NOT NULL,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX idx_policy_embedding ON policy_documents
            USING ivfflat (embedding vector_cosine_ops);

            CREATE INDEX idx_policy_doc ON policy_documents(document_name);
            """

            for stmt in sql.split(";"):
                if stmt.strip():
                    conn.execute(text(stmt))
            conn.commit()
            print("[SUCCESS] policy_documents table created with correct schema!")
            print("[INFO] Columns: id, document_name, page_number, chunk_number, section, content, embedding")

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
