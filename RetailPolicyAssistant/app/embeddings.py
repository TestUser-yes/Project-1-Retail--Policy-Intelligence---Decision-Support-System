from __future__ import annotations

import hashlib
import os
import re

import numpy as np

EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "fallback").lower()

# Optional: Try Ollama only if explicitly enabled
try:
    from langchain_community.embeddings import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def _fallback_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """
    Deterministic local embedding - NO external dependencies needed.

    Works completely offline. Same query always produces same embedding.
    Perfect for development, testing, and systems without external services.

    Dimensions: 1536 (compatible with pgvector)
    """
    vector = np.zeros(dimensions, dtype=float)
    tokens = re.findall(r"[a-z0-9]+", text.lower())

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % dimensions
        vector[index] += 1.0

    norm = np.linalg.norm(vector)
    if norm:
        vector = vector / norm

    return vector.tolist()


def _get_ollama_embedding(text: str) -> list[float]:
    """
    Optional: Get semantic embedding from Ollama local model.
    Only used if OLLAMA_MODEL env var is set.
    """
    try:
        model = os.getenv("OLLAMA_MODEL", "").strip()
        if not model:
            return _fallback_embedding(text)

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        embeddings = OllamaEmbeddings(model=model, base_url=base_url)
        embedding = embeddings.embed_query(text)
        return embedding
    except Exception as e:
        print(f"Ollama unavailable: {e}. Using local fallback embedding.")
        return _fallback_embedding(text)


def get_embedding(text: str) -> list[float]:
    """
    Convert text → 1536-dim vector embedding.

    NO EXTERNAL DEPENDENCIES REQUIRED - Works completely offline!

    Modes:
    1. Fallback (DEFAULT) - Pure local, deterministic, no external services
       - Set: EMBEDDING_MODE=fallback
       - ✅ Works everywhere (no downloads needed)
       - ✅ Reproducible (same text = same embedding)
       - ✅ Fast (no network calls)
       - ✅ Perfect for development/testing

    2. Ollama (OPTIONAL) - Local AI model
       - Set: OLLAMA_MODEL=<model_name>
       - Set: OLLAMA_BASE_URL=http://localhost:11434
       - Only used if model and base_url are configured
       - Falls back to fallback mode if unavailable

    Usage:
    - Default: Just works! No config needed
    - With Ollama: Set OLLAMA_MODEL env var
    - Force fallback: Set EMBEDDING_MODE=fallback
    """
    # Check if using fallback-only mode
    if EMBEDDING_MODE == "fallback":
        return _fallback_embedding(text)

    # Try Ollama if available and configured
    if OLLAMA_AVAILABLE and os.getenv("OLLAMA_MODEL", "").strip():
        return _get_ollama_embedding(text)

    # Default fallback for all other cases
    return _fallback_embedding(text)
