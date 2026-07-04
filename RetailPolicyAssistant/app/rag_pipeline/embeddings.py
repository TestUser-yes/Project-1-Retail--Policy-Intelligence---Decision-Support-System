"""Embeddings - Step 2 of RAG pipeline: Convert text to embeddings."""

import numpy as np


class EmbeddingService:
    """Generates embeddings for text."""

    def __init__(self, model: str = "ollama"):
        self.model = model

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a query."""
        # TODO: Implement embedding via Ollama or API
        return np.random.randn(384)

    def embed_documents(self, documents: list[str]) -> list[np.ndarray]:
        """Embed multiple documents."""
        return [self.embed_query(doc) for doc in documents]

    def embed_text(self, text: str) -> dict:
        """Embed text and return metadata."""
        embedding = self.embed_query(text)
        return {
            "text": text,
            "embedding": embedding,
            "dimension": len(embedding),
            "model": self.model,
        }
