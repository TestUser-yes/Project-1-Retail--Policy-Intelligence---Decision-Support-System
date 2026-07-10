from pathlib import Path
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.embeddings import get_embedding
from app.models import PolicyDocument
from app.database.session import SessionLocal

DOCUMENTS_DIR = Path("Documents")


def index_pdf_file(pdf_file_path: str) -> dict:
    """
    Index a single PDF file: load, split, embed, and store chunks in PostgreSQL.

    Args:
        pdf_file_path: Full path to PDF file

    Returns:
        dict with:
            - filename: str (original filename)
            - document_name: str (same as filename)
            - chunks_created: int (number of chunks indexed)
            - total_pages: int (number of pages in PDF)
            - timestamp: str (ISO format timestamp)
            - status: str ("indexed" for success)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    pdf_path = Path(pdf_file_path)
    filename = pdf_path.name
    db = SessionLocal()

    try:
        print(f"Indexing PDF: {filename}")

        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        total_pages = len(pages)
        chunk_number = 0

        for page in pages:
            chunks = splitter.split_text(page.page_content)

            for chunk in chunks:
                record = PolicyDocument(
                    document_name=filename,
                    page_number=page.metadata.get("page", 0) + 1,
                    chunk_number=chunk_number,
                    section="",
                    content=chunk,
                    embedding=get_embedding(chunk),
                )
                db.add(record)
                chunk_number += 1

        db.commit()

        result = {
            "filename": filename,
            "document_name": filename,
            "chunks_created": chunk_number,
            "total_pages": total_pages,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "indexed",
        }

        print(f"[SUCCESS] Indexed {filename}: {chunk_number} chunks from {total_pages} pages")
        return result

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to index {filename}: {str(e)}")
        raise
    finally:
        db.close()


def index_documents() -> None:
    """
    Batch index all PDFs from the Documents folder.
    Clears existing index before re-indexing (development use).
    """
    db = SessionLocal()

    try:
        # Clear old index before re-indexing
        db.query(PolicyDocument).delete()
        db.commit()
        print("Cleared existing policy documents index.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):
        try:
            index_pdf_file(str(pdf_path))
        except Exception as e:
            print(f"[WARNING] Skipped {pdf_path.name}: {str(e)}")
            continue

    print("[SUCCESS] Batch document indexing completed.")