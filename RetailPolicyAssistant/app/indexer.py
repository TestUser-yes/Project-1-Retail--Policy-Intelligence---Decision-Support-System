from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.database.session import SessionLocal
from app.embeddings import get_embedding
from app.models import PolicyDocument


DOCUMENTS_DIR = Path(__file__).resolve().parents[1] / "Documents"


def index_documents():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    db = SessionLocal()

    try:
        for pdf in DOCUMENTS_DIR.glob("*.pdf"):
            loader = PyPDFLoader(str(pdf))
            pages = loader.load()

            chunk_number = 0

            for page in pages:
                chunks = splitter.split_text(page.page_content)

                for chunk in chunks:
                    record = PolicyDocument(
                        document_name=pdf.name,
                        page_number=page.metadata.get("page", 0) + 1,
                        chunk_number=chunk_number,
                        section="",
                        content=chunk,
                        embedding=get_embedding(chunk),
                    )

                    db.add(record)
                    chunk_number += 1

        db.commit()

    finally:
        db.close()

