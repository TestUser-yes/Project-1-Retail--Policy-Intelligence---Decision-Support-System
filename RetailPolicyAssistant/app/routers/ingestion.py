"""Data Ingestion & Retrieval Endpoints - Phase 1 & 2 of RAG Flow

Phase 1 (Data Ingestion):  PDF Upload → Load → Split → Embed → Store
Phase 2 (Data Retrieval):  Query → Embed → Vector Search → Return Chunks
"""

import tempfile
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.indexer import index_pdf_file
from app.rag.retriever import retrieve_policy_chunks
from app.database.session import get_db
from app.core.auth import get_current_user, User
from app.core.permissions import PermissionValidator, Permission
from app.observability.langfuse_tracer import get_tracer


router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class IngestRequest(BaseModel):
    """Request for document ingestion endpoint."""
    pass


class IngestResponse(BaseModel):
    """Response for document ingestion endpoint."""
    filename: str = Field(..., description="Name of uploaded PDF file")
    document_name: str = Field(..., description="Document name in database")
    chunks_created: int = Field(..., description="Number of chunks created")
    total_pages: int = Field(..., description="Number of pages in PDF")
    status: str = Field(..., description="Ingestion status: indexed, error, etc.")
    timestamp: str = Field(..., description="ISO format timestamp")


class RetrieveRequest(BaseModel):
    """Request for document retrieval endpoint."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    k: int = Field(default=6, ge=1, le=20, description="Top-k chunks to retrieve")


class ChunkMetadata(BaseModel):
    """Metadata for a retrieved chunk."""
    id: int = Field(..., description="Chunk ID in database")
    document_name: str = Field(..., description="Source document name")
    page_number: int = Field(..., description="Page number in source document")
    section: str = Field(default="", description="Section heading (if available)")
    chunk_number: int = Field(..., description="Chunk index within document")


class ChunkData(BaseModel):
    """Retrieved document chunk with metadata."""
    content: str = Field(..., description="Chunk text content")
    metadata: ChunkMetadata


class RetrieveResponse(BaseModel):
    """Response for document retrieval endpoint."""
    query: str = Field(..., description="Original search query")
    chunks: list[ChunkData] = Field(..., description="Retrieved chunks with metadata")
    count: int = Field(..., description="Number of chunks retrieved")
    timestamp: str = Field(..., description="ISO format timestamp")
    # Multi-agent retrieval details (Level 2)
    retrieval_method: str = Field(default="multi_agent", description="Retrieval method used")
    retrieval_agents: list[str] = Field(default_factory=list, description="Agents used in retrieval")
    retrieval_pipeline: dict = Field(default_factory=dict, description="Full retrieval pipeline execution details")


# ============================================================================
# PHASE 1: DATA INGESTION ENDPOINT
# ============================================================================

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request: Request,
    file: UploadFile = File(..., description="PDF file to ingest"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and index a PDF document.

    Phase 1 of RAG Flow:
    1. Load PDF from upload
    2. Split into chunks (1000 chars, 200 overlap)
    3. Generate embeddings for each chunk
    4. Store in PostgreSQL with pgvector

    Returns:
        IngestResponse with ingestion status and metadata
    """
    tracer = get_tracer()

    try:
        # Check permission
        PermissionValidator.assert_permission(
            current_user,
            Permission.ASK_POLICY_QUESTION  # Users with policy access can upload
        )

        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported",
            )

        tracer.log_event("ingest_start", {"filename": file.filename, "user_id": current_user.user_id})

        # Save uploaded file to temporary location
        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            dir="Documents"  # Store in Documents folder
        ) as tmp_file:
            tmp_file.write(contents)
            tmp_path = tmp_file.name

        # Index the PDF file
        result = index_pdf_file(tmp_path)

        # Log success
        tracer.log_event(
            "ingest_complete",
            {
                "filename": file.filename,
                "chunks": result["chunks_created"],
                "pages": result["total_pages"],
            }
        )

        return IngestResponse(
            filename=file.filename,
            document_name=result["document_name"],
            chunks_created=result["chunks_created"],
            total_pages=result["total_pages"],
            status=result["status"],
            timestamp=result["timestamp"],
        )

    except HTTPException:
        raise
    except Exception as e:
        tracer.log_error("ingest_error", str(e)[:200])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)[:100]}",
        )
    finally:
        tracer.flush()


# ============================================================================
# PHASE 2: DATA RETRIEVAL ENDPOINT
# ============================================================================

@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_documents(
    request_data: RetrieveRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve relevant document chunks using vector similarity search.

    Updated to use multi-agent retrieval with semantic + keyword agents.

    Phase 2 of RAG Flow:
    1. Embed user query
    2. Vector similarity search (pgvector)
    3. Return top-k most relevant chunks

    Args:
        request: RetrieveRequest with query and k

    Returns:
        RetrieveResponse with ranked chunks and metadata
    """
    tracer = get_tracer()

    try:
        # Check permission
        PermissionValidator.assert_permission(
            current_user,
            Permission.ASK_POLICY_QUESTION
        )

        tracer.log_event(
            "retrieve_start",
            {"query": request_data.query[:100], "k": request_data.k, "user_id": current_user.user_id}
        )

        # Retrieve chunks using multi-agent retrieval
        from app.rag.multi_agent_retrieval import retrieve_with_multi_agent
        import io
        import sys
        import contextlib

        # Suppress Unicode printing from multi-agent retrieval (Windows console compatibility)
        with contextlib.redirect_stdout(io.StringIO()):
            retrieval_result = retrieve_with_multi_agent(request_data.query, top_k=request_data.k * 2)
        chunks = retrieval_result.get("documents", [])
        retrieval_method = retrieval_result.get("retrieval_method", "multi_agent")
        retrieval_agents = retrieval_result.get("agents_used", [])
        retrieval_pipeline = retrieval_result.get("retrieval_pipeline", {})

        if not chunks:
            return RetrieveResponse(
                query=request_data.query,
                chunks=[],
                count=0,
                timestamp=datetime.utcnow().isoformat(),
                retrieval_method=retrieval_method,
                retrieval_agents=retrieval_agents,
                retrieval_pipeline=retrieval_pipeline,
            )

        # Format chunks with metadata
        chunk_data = []
        for chunk in chunks[:request_data.k]:  # Limit to requested k
            metadata = ChunkMetadata(
                id=chunk.id,
                document_name=chunk.document_name,
                page_number=chunk.page_number,
                section=chunk.section or "",
                chunk_number=chunk.chunk_number,
            )
            chunk_data.append(
                ChunkData(
                    content=chunk.content,
                    metadata=metadata,
                )
            )

        # Log success
        tracer.log_event(
            "retrieve_complete",
            {"query": request_data.query[:100], "chunks_retrieved": len(chunk_data)}
        )

        return RetrieveResponse(
            query=request_data.query,
            chunks=chunk_data,
            count=len(chunk_data),
            timestamp=datetime.utcnow().isoformat(),
            retrieval_method=retrieval_method,
            retrieval_agents=retrieval_agents,
            retrieval_pipeline=retrieval_pipeline,
        )

    except HTTPException:
        raise
    except Exception as e:
        tracer.log_error("retrieve_error", str(e)[:200])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)[:100]}",
        )
    finally:
        tracer.flush()
