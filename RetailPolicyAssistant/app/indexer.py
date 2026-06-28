from __future__ import annotations

from app.embeddings import get_embedding
from app.models.policy import PolicyDocument
from app.database.session import SessionLocal


def index_documents(docs: list[str]) -> None:
    """Store documents and embeddings into the pgvector-backed database."""
    db = SessionLocal()
    try:
        for doc in docs:
            embedding = get_embedding(doc)
            record = PolicyDocument(content=doc, embedding=embedding)
            db.add(record)
        db.commit()
    finally:
        db.close()
