from app.embeddings import get_embedding
from app.models import PolicyDocument
from app.session import SessionLocal


def retrieve_policy_chunks(question: str, top_k: int = 6):
    """
    Retrieve the most relevant policy chunks using pgvector similarity search.
    """
    db = SessionLocal()
    try:
        embedding = get_embedding(question)
        results = (
            db.query(PolicyDocument)
            .order_by(PolicyDocument.embedding.l2_distance(embedding))
            .limit(top_k * 2)
            .all()
        )
        return results
    finally:
        db.close()
