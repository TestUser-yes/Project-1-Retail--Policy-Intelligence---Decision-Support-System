"""Index PDF documents from Documents folder into the database."""

import os
from dotenv import load_dotenv

load_dotenv()

from app.indexer import index_documents

if __name__ == "__main__":
    print("[INFO] Starting document indexing from PDFs...")
    print("[INFO] Looking for PDFs in: Documents/")

    try:
        result = index_documents()
        print(f"[SUCCESS] Document indexing completed!")
        print(f"[INFO] {result}")

    except Exception as e:
        print(f"[ERROR] Document indexing failed: {e}")
        import traceback
        traceback.print_exc()
