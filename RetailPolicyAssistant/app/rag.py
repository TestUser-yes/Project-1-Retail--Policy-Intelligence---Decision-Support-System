from __future__ import annotations

from pydantic import BaseModel

from app.embeddings import get_embedding
from app.models.policy import PolicyDocument
from app.database.session import SessionLocal


class SourceChunk(BaseModel):
    source: str
    section: str
    text: str


class RAGResult(BaseModel):
    answer: str
    confidence: float
    sources: list[SourceChunk]


NOT_FOUND_MESSAGE = "I couldn't find that information in the company policy."


def answer_rag(query: str):
    """REAL pgvector similarity search against stored policy documents."""
    db = SessionLocal()
    query_embedding = get_embedding(query)

    try:
        results = (
            db.query(PolicyDocument)
            .order_by(PolicyDocument.embedding.l2_distance(query_embedding))
            .limit(3)
            .all()
        )

        if not results:
            return "No relevant policy found."

        return "\n".join(record.content for record in results)
    finally:
        db.close()


def answer_from_policy_context(question: str) -> RAGResult:
    db = SessionLocal()
    query_embedding = get_embedding(question)

    try:
        results = (
            db.query(PolicyDocument)
            .order_by(PolicyDocument.embedding.l2_distance(query_embedding))
            .limit(1)
            .all()
        )
    finally:
        db.close()

    if not results:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    best_doc = results[0]
    return RAGResult(
        answer=best_doc.content,
        confidence=0.0,
        sources=[
            SourceChunk(
                source="documents",
                section=f"doc-{best_doc.id}",
                text=best_doc.content,
            )
        ],
    )
