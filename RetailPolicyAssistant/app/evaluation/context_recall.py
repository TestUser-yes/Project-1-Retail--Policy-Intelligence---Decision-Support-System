"""Context Recall Evaluator - Measures completeness of retrieved documents."""

from typing import List, Dict, Any, Optional
import re
from math import sqrt


class ContextRecallEvaluator:
    """Evaluates context recall - completeness of retrieved documents."""

    def __init__(self):
        """Initialize evaluator."""
        pass

    def evaluate_recall(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        route: str = "rag"
    ) -> float:
        """Evaluate context recall for retrieved chunks.

        Measures: Did we retrieve all relevant information for this query?

        Args:
            query: User's query text
            retrieved_chunks: List of retrieved document chunks
            route: Query route (rag, sql, hybrid)

        Returns:
            Recall score from 0.0 to 1.0
        """
        if not retrieved_chunks:
            return 0.0

        if route == "sql":
            return self._evaluate_recall_sql(query, retrieved_chunks)
        elif route == "rag":
            return self._evaluate_recall_rag(query, retrieved_chunks)
        elif route == "hybrid":
            sql_score = self._evaluate_recall_sql(query, retrieved_chunks)
            rag_score = self._evaluate_recall_rag(query, retrieved_chunks)
            return (sql_score + rag_score) / 2.0
        else:
            return self._evaluate_recall_rag(query, retrieved_chunks)

    def _evaluate_recall_sql(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """Evaluate recall for SQL route - coverage of relevant data types.

        Args:
            query: User query
            retrieved_chunks: Retrieved documents

        Returns:
            Recall score
        """
        if not retrieved_chunks:
            return 0.0

        query_lower = query.lower()
        doc_count = len(retrieved_chunks)

        # Track what kinds of documents were retrieved
        has_policy = False
        has_vendor = False
        has_compliance = False
        has_sla = False
        section_diversity = set()

        for chunk in retrieved_chunks:
            doc_name = (chunk.get("document") or chunk.get("document_name") or "").lower()
            section = (chunk.get("section") or "").lower()

            if "vendor" in doc_name or "vendor" in section:
                has_vendor = True
            if "policy" in doc_name or "policy" in section:
                has_policy = True
            if "compliance" in doc_name or "compliance" in section:
                has_compliance = True
            if "sla" in doc_name or "sla" in section:
                has_sla = True

            section_diversity.add(section)

        # Score based on query intent and coverage
        intent_score = 0.5

        if "vendor" in query_lower:
            intent_score = 0.9 if has_vendor else 0.5
        elif "policy" in query_lower:
            intent_score = 0.9 if has_policy else 0.5
        elif "compliance" in query_lower:
            intent_score = 0.9 if has_compliance else 0.6
        elif "sla" in query_lower:
            intent_score = 0.9 if has_sla else 0.5
        else:
            # Generic query - check for multiple types
            types_found = sum([has_policy, has_vendor, has_compliance, has_sla])
            intent_score = 0.6 + (types_found * 0.1)

        # Document count score (more docs = better coverage)
        doc_count_score = min(1.0, doc_count / 5.0)  # Good if 5+ docs

        # Section diversity score (more diverse sections = better coverage)
        diversity_score = min(1.0, len(section_diversity) / 3.0)  # Good if 3+ sections

        # Combine scores
        recall = (intent_score * 0.5) + (doc_count_score * 0.3) + (diversity_score * 0.2)
        return min(1.0, max(0.0, recall))

    def _evaluate_recall_rag(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """Evaluate recall for RAG route - semantic diversity of results.

        Args:
            query: User query
            retrieved_chunks: Retrieved documents

        Returns:
            Recall score
        """
        if not retrieved_chunks:
            return 0.0

        if len(retrieved_chunks) < 2:
            # Single document retrieved - acceptable but limited
            return 0.7

        doc_count = len(retrieved_chunks)

        # 1. Section diversity check
        sections = set()
        for chunk in retrieved_chunks:
            section = chunk.get("section") or ""
            if section:
                sections.add(section)

        # Good recall if multiple sections covered
        section_diversity_score = min(1.0, len(sections) / 3.0)

        # 2. Document diversity check
        documents = set()
        for chunk in retrieved_chunks:
            doc = chunk.get("document") or chunk.get("document_name") or ""
            if doc:
                documents.add(doc)

        # Good recall if multiple documents
        doc_diversity_score = min(1.0, len(documents) / 2.0)

        # 3. Content similarity check (penalize near-duplicates)
        similarity_penalty = self._calculate_similarity_penalty(retrieved_chunks)

        # 4. Document count check
        doc_count_score = min(1.0, doc_count / 6.0)  # Good if 6+ docs

        # Combine scores
        recall = (
            (section_diversity_score * 0.25) +
            (doc_diversity_score * 0.25) +
            ((1.0 - similarity_penalty) * 0.25) +
            (doc_count_score * 0.25)
        )

        return min(1.0, max(0.0, recall))

    def _calculate_similarity_penalty(
        self,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """Calculate penalty for retrieving very similar documents.

        Low similarity between chunks = better recall (diverse info).
        High similarity between chunks = worse recall (redundant info).

        Args:
            retrieved_chunks: Retrieved documents

        Returns:
            Penalty score 0.0-1.0 (higher = worse diversity)
        """
        if len(retrieved_chunks) < 2:
            return 0.0

        # Get content from chunks
        contents = []
        for chunk in retrieved_chunks:
            content = chunk.get("content") or ""
            if content:
                # Normalize: lowercase, remove punctuation
                content_norm = re.sub(r'[^a-z0-9\s]', '', content.lower())
                contents.append(content_norm)

        if len(contents) < 2:
            return 0.0

        # Calculate average pairwise similarity using simple word overlap
        total_similarity = 0.0
        pair_count = 0

        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                similarity = self._text_similarity(contents[i], contents[j])
                total_similarity += similarity
                pair_count += 1

        if pair_count == 0:
            return 0.0

        avg_similarity = total_similarity / pair_count

        # Convert similarity to penalty (high similarity = high penalty)
        # Clamp to 0-1: similarity > 0.7 is heavily penalized
        if avg_similarity > 0.7:
            return min(1.0, (avg_similarity - 0.7) * 2.0)  # Steep penalty
        elif avg_similarity > 0.5:
            return (avg_similarity - 0.5) * 0.5  # Medium penalty
        else:
            return 0.0  # No penalty for diverse content

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using word overlap.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score 0.0-1.0
        """
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        # Jaccard similarity
        similarity = intersection / union
        return min(1.0, max(0.0, similarity))
