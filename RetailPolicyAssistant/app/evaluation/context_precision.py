"""Context Precision Evaluator - Measures relevance of retrieved documents."""

from typing import List, Dict, Any, Optional
import re
from collections import Counter


class ContextPrecisionEvaluator:
    """Evaluates context precision - relevance of retrieved chunks to query."""

    def __init__(self):
        """Initialize evaluator."""
        self.stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "do", "does", "did", "will", "would", "could", "should", "may",
            "might", "must", "can", "as", "by", "from", "with", "about", "into",
        }

    def evaluate_precision(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        route: str = "rag"
    ) -> float:
        """Evaluate context precision for retrieved chunks.

        Measures: What fraction of retrieved documents are relevant to the query?

        Args:
            query: User's query text
            retrieved_chunks: List of retrieved document chunks with metadata
            route: Query route (rag, sql, hybrid)

        Returns:
            Precision score from 0.0 to 1.0
        """
        if not retrieved_chunks:
            return 0.0

        # Extract query keywords
        query_keywords = self._extract_keywords(query)
        if not query_keywords:
            # If no meaningful keywords, default to medium precision
            return 0.65

        # Score each chunk
        chunk_scores = []
        for chunk in retrieved_chunks:
            score = self._score_chunk(chunk, query_keywords, query, route)
            chunk_scores.append(score)

        # Precision = average relevance of all retrieved chunks
        if not chunk_scores:
            return 0.5

        precision = sum(chunk_scores) / len(chunk_scores)
        return min(1.0, max(0.0, precision))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text.

        Args:
            text: Input text

        Returns:
            List of keywords (lowercased, deduplicated)
        """
        # Convert to lowercase and extract words
        text_lower = text.lower()
        # Remove special characters but keep spaces
        text_clean = re.sub(r'[^a-z0-9\s]', ' ', text_lower)
        # Split into words
        words = text_clean.split()
        # Filter stopwords and short words, keep unique
        keywords = [w for w in words if w not in self.stopwords and len(w) > 2]
        return list(set(keywords))

    def _score_chunk(
        self,
        chunk: Dict[str, Any],
        query_keywords: List[str],
        query: str,
        route: str
    ) -> float:
        """Score a single chunk for relevance to query.

        Args:
            chunk: Chunk metadata and content
            query_keywords: Extracted query keywords
            query: Original query text
            route: Query route

        Returns:
            Relevance score from 0.0 to 1.0
        """
        base_score = 0.0

        # 1. Keyword overlap (40% weight)
        content = chunk.get("content", "") or ""
        if content:
            chunk_keywords = self._extract_keywords(content)
            matching_keywords = len(set(query_keywords) & set(chunk_keywords))
            keyword_score = matching_keywords / max(len(query_keywords), 1)
            base_score += keyword_score * 0.40

        # 2. Section relevance (30% weight)
        section = (chunk.get("section") or "").lower()
        section_score = self._score_section_relevance(section, query_keywords, query, route)
        base_score += section_score * 0.30

        # 3. Document type relevance (20% weight)
        doc_name = (chunk.get("document") or chunk.get("document_name") or "").lower()
        doc_score = self._score_document_relevance(doc_name, query_keywords, query, route)
        base_score += doc_score * 0.20

        # 4. Retrieval score if available (10% weight)
        if "retrieval_score" in chunk or "score" in chunk:
            retrieval_score = chunk.get("retrieval_score") or chunk.get("score") or 0.0
            if isinstance(retrieval_score, (int, float)) and retrieval_score > 0:
                base_score += min(retrieval_score / 1.0, 1.0) * 0.10

        return min(1.0, max(0.0, base_score))

    def _score_section_relevance(
        self,
        section: str,
        query_keywords: List[str],
        query: str,
        route: str
    ) -> float:
        """Score section relevance to query.

        Args:
            section: Section name/title
            query_keywords: Query keywords
            query: Original query
            route: Query route

        Returns:
            Section relevance score 0.0-1.0
        """
        if not section:
            return 0.5  # Default for missing section

        # Check for keyword matches in section
        section_keywords = self._extract_keywords(section)
        matching = len(set(query_keywords) & set(section_keywords))
        keyword_match_score = matching / max(len(query_keywords), 1) if query_keywords else 0.5

        # Route-specific section scoring
        route_score = 0.5
        if route == "sql":
            # For SQL, prefer sections about vendor/data/compliance
            if any(w in section for w in ["vendor", "data", "compliance", "requirement", "policy", "sla"]):
                route_score = 0.9
        elif route == "rag":
            # For RAG, prefer sections about policies and procedures
            if any(w in section for w in ["policy", "procedure", "requirement", "rule", "standard", "process"]):
                route_score = 0.9

        # Combine scores
        combined = (keyword_match_score * 0.6) + (route_score * 0.4)
        return min(1.0, max(0.0, combined))

    def _score_document_relevance(
        self,
        doc_name: str,
        query_keywords: List[str],
        query: str,
        route: str
    ) -> float:
        """Score document relevance to query.

        Args:
            doc_name: Document file name
            query_keywords: Query keywords
            query: Original query
            route: Query route

        Returns:
            Document relevance score 0.0-1.0
        """
        if not doc_name:
            return 0.5

        # Check keyword matches in document name
        doc_keywords = self._extract_keywords(doc_name)
        matching = len(set(query_keywords) & set(doc_keywords))
        keyword_score = matching / max(len(query_keywords), 1) if query_keywords else 0.5

        # Route-specific preferences
        route_score = 0.5
        if route == "sql":
            if any(word in doc_name for word in ["vendor", "contract", "sla", "requirement"]):
                route_score = 0.9
        elif route == "rag":
            if any(word in doc_name for word in ["policy", "procedure", "standard", "guideline"]):
                route_score = 0.9
        elif route == "hybrid":
            if any(word in doc_name for word in ["policy", "procedure", "vendor", "standard"]):
                route_score = 0.85

        # Combine scores
        combined = (keyword_score * 0.7) + (route_score * 0.3)
        return min(1.0, max(0.0, combined))
