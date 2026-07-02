from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

DOCUMENTS_DIR = Path("Documents")


def load_policy_documents():
    """
    Load all policy PDFs from the Documents folder.
    """
    documents = []
    for pdf_file in DOCUMENTS_DIR.glob("*.pdf"):
        print(f"Loading {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()
        for page in pages:
            page.metadata["document_name"] = pdf_file.name
        documents.extend(pages)
    return documents
