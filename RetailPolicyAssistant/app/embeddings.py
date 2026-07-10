from __future__ import annotations

import hashlib
import os
import re

import numpy as np

try:
    from langchain_community.embeddings import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def _fallback_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """
    Deterministic local embedding used when Ollama unavailable.
    Provides consistent hashing-based embeddings for consistency.
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
    """Get semantic embedding from Ollama local model."""
    try:
        model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        embeddings = OllamaEmbeddings(model=model, base_url=base_url)
        embedding = embeddings.embed_query(text)
        return embedding
    except Exception as e:
        print(f"Ollama embedding failed: {e}. Falling back to local embedding.")
        return _fallback_embedding(text)


def get_embedding(text: str) -> list[float]:
    """
    Convert text → vector embedding using Ollama local model.

    Priority:
    1. Ollama (local, fast, good quality)
    2. Fallback hash-based (deterministic, no external dependencies)

    Note: Project uses only Ollama embeddings, no external API calls.
    """
    # Try Ollama first
    if OLLAMA_AVAILABLE and os.getenv("OLLAMA_MODEL", "").strip():
        return _get_ollama_embedding(text)

    # Fallback to deterministic hash-based embedding
    return _fallback_embedding(text)
