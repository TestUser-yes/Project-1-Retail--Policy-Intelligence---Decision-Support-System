from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.embeddings import get_embedding
from app.models import PolicyDocument
from app.database.session import SessionLocal

DOCUMENTS_DIR = Path("Documents")


def index_documents() -> None:
    """
    Reads all PDFs from the Documents folder,
    splits them into chunks,
    generates embeddings,
    and stores them in PostgreSQL.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    db = SessionLocal()

    try:
        # Optional during development: avoid duplicate indexing
        db.query(PolicyDocument).delete()

        for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):

            print(f"Indexing: {pdf_path.name}")

            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()

            chunk_number = 0

            for page in pages:

                chunks = splitter.split_text(page.page_content)

                for chunk in chunks:

                    record = PolicyDocument(
                        document_name=pdf_path.name,
                        page_number=page.metadata.get("page", 0) + 1,
                        chunk_number=chunk_number,
                        section="",
                        content=chunk,
                        embedding=get_embedding(chunk),
                    )

                    db.add(record)
                    chunk_number += 1

        db.commit()

        print("✅ Document indexing completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()