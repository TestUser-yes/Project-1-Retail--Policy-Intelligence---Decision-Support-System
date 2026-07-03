from __future__ import annotations

from app.embeddings import get_embedding
from app.models import PolicyDocument
from app.rag.loader import load_policy_documents
from app.rag.splitter import split_documents
from app.database.session import SessionLocal


def ingest_documents() -> None:
    """
    Load PDFs, split into chunks, generate embeddings,
    and store everything in PostgreSQL.
    """
    print("=" * 60)
    print("Loading policy documents...")
    print("=" * 60)
    documents = load_policy_documents()
    chunks = split_documents(documents)
    print(f"Loaded {len(documents)} pages")
    print(f"Created {len(chunks)} chunks")

    db = SessionLocal()
    try:
        # Optional: clear old index before re-indexing
        db.query(PolicyDocument).delete()
        for chunk_number, chunk in enumerate(chunks, start=1):
            page_number = chunk.metadata.get("page", 0) + 1
            document_name = chunk.metadata.get(
                "document_name",
                "Unknown Document",
            )
            section = chunk.metadata.get("section", "")
            embedding = get_embedding(chunk.page_content)
            record = PolicyDocument(
                document_name=document_name,
                page_number=page_number,
                chunk_number=chunk_number,
                section=section,
                content=chunk.page_content,
                embedding=embedding,
            )
            db.add(record)
            if chunk_number % 25 == 0:
                print(f"Indexed {chunk_number} chunks...")

        db.commit()
        print("=" * 60)
        print("Indexing completed successfully.")
        print(f"Stored {len(chunks)} chunks.")
        print("=" * 60)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
