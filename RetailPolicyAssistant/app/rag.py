from __future__ import annotations

from pydantic import BaseModel
from pgvector.sqlalchemy import Vector

from app.embeddings import get_embedding
from app.models import PolicyDocument
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
        if not query_embedding:
            return "No relevant policy found."

        results = (
            db.query(PolicyDocument)
            .filter(PolicyDocument.embedding.isnot(None))
            .order_by(PolicyDocument.embedding.l2_distance(query_embedding))
            .limit(3)
            .all()
        )

        if not results:
            return "No relevant policy found."

        return "\n".join(record.content for record in results)
    except Exception as e:
        print(f"RAG query error: {e}")
        return f"Error retrieving policies: {str(e)}"
    finally:
        db.close()


def answer_from_policy_context(question: str) -> RAGResult:
    db = SessionLocal()
    query_embedding = get_embedding(question)

    try:
        if not query_embedding:
            return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

        results = (
            db.query(PolicyDocument)
            .filter(PolicyDocument.embedding.isnot(None))
            .order_by(PolicyDocument.embedding.l2_distance(query_embedding))
            .limit(1)
            .all()
        )

        if not results:
            return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])
    except Exception as e:
        print(f"Policy context query error: {e}")
        return RAGResult(answer=f"Error: {str(e)}", confidence=0.0, sources=[])
    finally:
        db.close()

    best_doc = results[0]
    source_section = best_doc.section or f"{best_doc.document_name} p.{best_doc.page_number} chunk {best_doc.chunk_number}"
    return RAGResult(
        answer=best_doc.content,
        confidence=0.0,
        sources=[
            SourceChunk(
                source="documents",
                section=source_section,
                text=best_doc.content,
            )
        ],
    )
