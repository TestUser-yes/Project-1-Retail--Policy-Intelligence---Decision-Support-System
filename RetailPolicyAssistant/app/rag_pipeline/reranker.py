"""Reranker - Step 4 of RAG pipeline: Score and rerank retrieved documents."""


class Reranker:
    """Reranks retrieved documents by relevance."""

    def __init__(self):
        self.threshold = 0.3

    def score_relevance(self, query: str, document: str) -> float:
        """Score document relevance to query."""
        # TODO: Implement semantic similarity scoring
        return 0.5

    def rerank(self, query: str, documents: list, top_k: int = 5) -> list:
        """Rerank documents by relevance score."""
        scored = [
            (doc, self.score_relevance(query, doc))
            for doc in documents
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored if score >= self.threshold][:top_k]

    def filter_low_relevance(self, documents: list, threshold: float = 0.3) -> list:
        """Filter out low-relevance documents."""
        return [doc for doc in documents if doc.get("score", 0) >= threshold]
