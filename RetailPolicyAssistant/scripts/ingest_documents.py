#!/usr/bin/env python
"""
Document Ingestion Script for Retail Policy Intelligence System
============================================

This script performs the complete document ingestion pipeline:
1. Scans Documents/ directory for PDFs
2. Loads and splits documents into chunks
3. Generates embeddings for each chunk
4. Stores chunks with embeddings in PostgreSQL vector store
5. Validates ingestion and reports statistics

Usage:
    python ingest_documents.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.indexer import index_documents
from app.database.session import SessionLocal
from app.models import PolicyDocument


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def validate_ingestion():
    """Validate that documents were successfully ingested."""
    db = SessionLocal()
    try:
        total_docs = db.query(PolicyDocument).count()

        if total_docs == 0:
            print("❌ ERROR: No documents found in database!")
            return False

        # Get statistics by document
        unique_docs = db.query(PolicyDocument.document_name).distinct().count()

        print(f"\n✅ Ingestion Validation Successful!")
        print(f"   Total Chunks: {total_docs}")
        print(f"   Unique Documents: {unique_docs}")

        # Show document breakdown
        print(f"\n   Document Breakdown:")
        doc_stats = db.query(
            PolicyDocument.document_name,
            db.func.count(PolicyDocument.id).label('chunks')
        ).group_by(PolicyDocument.document_name).all()

        for doc_name, chunk_count in doc_stats:
            print(f"     • {doc_name}: {chunk_count} chunks")

        return True
    finally:
        db.close()


def main():
    """Main ingestion workflow."""
    print_header("Retail Policy Intelligence - Document Ingestion")

    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Project Root: {project_root}")

    # Check Documents directory exists
    docs_dir = project_root / "Documents"
    if not docs_dir.exists():
        print(f"\n❌ ERROR: Documents directory not found at {docs_dir}")
        print("   Please create Documents/ folder and add PDF files.")
        return False

    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"\n⚠️  WARNING: No PDF files found in {docs_dir}")
        print("   Add policy PDF files to Documents/ folder to proceed.")
        return False

    print(f"\nFound {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"  • {pdf_file.name} ({pdf_file.stat().st_size / 1024:.1f} KB)")

    # Run ingestion
    print_header("Ingesting Documents")
    try:
        index_documents()
        print("\n✅ Document ingestion pipeline completed successfully!")
    except Exception as e:
        print(f"\n❌ ERROR during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Validate results
    print_header("Validating Ingestion")
    if not validate_ingestion():
        return False

    print_header("Ingestion Complete")
    print(f"Completed at: {datetime.now().isoformat()}")
    print("\nNext steps:")
    print("  1. Start the API server: python -m uvicorn app.main:app --reload")
    print("  2. Test with: curl -X POST http://localhost:8000/ask \\")
    print("               -H 'Content-Type: application/json' \\")
    print("               -d '{\"query\": \"What is the retention policy?\"}'")
    print("  3. Run evaluations: python -m app.evaluation.evaluator")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
