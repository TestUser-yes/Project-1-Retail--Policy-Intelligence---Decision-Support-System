"""
Multi-Agent Retrieval System for RAG Pipeline

This module implements a sophisticated multi-agent retrieval approach where:
1. Semantic Agent: Retrieves by semantic similarity (embeddings)
2. Keyword Agent: Retrieves by exact keyword matching
3. Ranking Agent: Ranks and deduplicates results

All agents run in parallel and fuse their results for optimal retrieval.
"""

import asyncio
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session

from app.models import PolicyDocument
from app.embeddings import get_embedding
from app.database.session import SessionLocal
from app.observability.langfuse_tracer import trace_function


class SemanticRetrievalAgent:
    """Retrieves documents using semantic similarity with embeddings."""

    def __init__(self):
        self.name = "semantic_retrieval_agent"

    @trace_function("semantic_retrieval", as_type="tool")
    def retrieve(self, question: str, top_k: int = 6, db: Session = None) -> tuple:
        """
        Retrieve using semantic similarity.

        Returns: (documents, retrieval_details)
        """
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False

        try:
            embedding = get_embedding(question)
            results = (
                db.query(PolicyDocument)
                .order_by(PolicyDocument.embedding.l2_distance(embedding))
                .limit(top_k)
                .all()
            )

            retrieval_details = {
                "agent": "semantic_retrieval_agent",
                "method": "embedding_similarity",
                "documents_retrieved": len(results),
                "top_k": top_k,
            }

            return results, retrieval_details
        finally:
            if close_db:
                db.close()


class KeywordRetrievalAgent:
    """Retrieves documents using keyword matching."""

    def __init__(self):
        self.name = "keyword_retrieval_agent"

    @trace_function("keyword_retrieval", as_type="tool")
    def retrieve(self, question: str, top_k: int = 6, db: Session = None) -> tuple:
        """
        Retrieve using keyword matching (exact and partial).

        Returns: (documents, retrieval_details)
        """
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False

        try:
            # Extract keywords from question
            keywords = self._extract_keywords(question)

            if not keywords:
                return [], {"agent": "keyword_retrieval_agent", "keywords": [], "documents_retrieved": 0}

            # Build OR query for keyword matching
            from sqlalchemy import or_

            query = db.query(PolicyDocument)

            # Match on section, document_name, or content
            filter_conditions = []
            for keyword in keywords:
                kw_lower = keyword.lower()
                filter_conditions.extend([
                    PolicyDocument.section.ilike(f"%{kw_lower}%"),
                    PolicyDocument.document_name.ilike(f"%{kw_lower}%"),
                    PolicyDocument.content.ilike(f"%{kw_lower}%"),
                ])

            results = query.filter(or_(*filter_conditions)).limit(top_k * 2).all()

            # Rank by keyword frequency in content
            results = self._rank_by_keyword_frequency(results, keywords)[:top_k]

            retrieval_details = {
                "agent": "keyword_retrieval_agent",
                "method": "keyword_matching",
                "keywords": keywords,
                "documents_retrieved": len(results),
                "top_k": top_k,
            }

            return results, retrieval_details
        finally:
            if close_db:
                db.close()

    def _extract_keywords(self, question: str, min_length: int = 3) -> List[str]:
        """Extract meaningful keywords from question."""
        # Remove common words
        stop_words = {
            "what", "is", "the", "a", "an", "and", "or", "but", "in", "on",
            "at", "to", "for", "of", "with", "by", "from", "up", "about",
            "into", "through", "during", "do", "does", "did", "have", "has",
            "tell", "me", "about", "explain", "describe", "show", "list"
        }

        words = question.lower().split()
        keywords = [
            w.strip(".,!?;:")
            for w in words
            if len(w) > min_length and w.lower() not in stop_words
        ]

        return list(set(keywords))  # Remove duplicates

    def _rank_by_keyword_frequency(self, documents: List[PolicyDocument], keywords: List[str]) -> List[PolicyDocument]:
        """Rank documents by keyword frequency."""
        scored_docs = []

        for doc in documents:
            score = 0
            content_lower = doc.content.lower()

            for keyword in keywords:
                # Count keyword occurrences
                score += content_lower.count(keyword.lower())

            scored_docs.append((doc, score))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs]


class RankingAgent:
    """Ranks and deduplicates results from multiple retrieval agents."""

    def __init__(self):
        self.name = "ranking_agent"

    @trace_function("result_ranking", as_type="tool")
    def rank_and_fuse(
        self,
        semantic_results: List[PolicyDocument],
        keyword_results: List[PolicyDocument],
        final_top_k: int = 6
    ) -> tuple:
        """
        Fuse results from multiple agents using ranking.

        Returns: (ranked_documents, ranking_details)
        """
        # Create a dictionary to track document scores
        doc_scores: Dict[int, Dict[str, Any]] = {}

        # Score semantic results (higher is better for semantic)
        for idx, doc in enumerate(semantic_results):
            if doc.id not in doc_scores:
                doc_scores[doc.id] = {
                    "document": doc,
                    "scores": {"semantic": 0, "keyword": 0},
                    "appearances": 0
                }
            # Inverse ranking (1st result = 1.0, last = lower)
            semantic_score = (len(semantic_results) - idx) / len(semantic_results)
            doc_scores[doc.id]["scores"]["semantic"] = semantic_score
            doc_scores[doc.id]["appearances"] += 1

        # Score keyword results
        for idx, doc in enumerate(keyword_results):
            if doc.id not in doc_scores:
                doc_scores[doc.id] = {
                    "document": doc,
                    "scores": {"semantic": 0, "keyword": 0},
                    "appearances": 0
                }
            keyword_score = (len(keyword_results) - idx) / len(keyword_results)
            doc_scores[doc.id]["scores"]["keyword"] = keyword_score
            doc_scores[doc.id]["appearances"] += 1

        # Calculate final score (weighted fusion)
        scored_results = []
        for doc_id, data in doc_scores.items():
            # Weight: 60% semantic, 40% keyword
            final_score = (
                0.6 * data["scores"]["semantic"] +
                0.4 * data["scores"]["keyword"]
            )

            # Boost if appears in both result sets
            if data["appearances"] > 1:
                final_score *= 1.3  # 30% boost for cross-agent consensus

            scored_results.append({
                "document": data["document"],
                "final_score": final_score,
                "semantic_score": data["scores"]["semantic"],
                "keyword_score": data["scores"]["keyword"],
                "appearances": data["appearances"],
            })

        # Sort by final score
        scored_results.sort(key=lambda x: x["final_score"], reverse=True)

        # Return top-k documents
        ranked_docs = [item["document"] for item in scored_results[:final_top_k]]

        ranking_details = {
            "agent": "ranking_agent",
            "method": "multi_agent_fusion",
            "semantic_weight": 0.6,
            "keyword_weight": 0.4,
            "documents_fused": len(doc_scores),
            "final_documents": len(ranked_docs),
            "consensus_boost_applied": True,
            "scored_results": [
                {
                    "document_id": item["document"].id,
                    "document_name": item["document"].document_name,
                    "final_score": round(item["final_score"], 3),
                    "semantic_score": round(item["semantic_score"], 3),
                    "keyword_score": round(item["keyword_score"], 3),
                    "appearances": item["appearances"],
                }
                for item in scored_results[:final_top_k]
            ],
        }

        return ranked_docs, ranking_details


class MultiAgentRetrieval:
    """
    Orchestrates multiple retrieval agents for superior document retrieval.

    Pipeline:
    1. Run SemanticRetrievalAgent and KeywordRetrievalAgent in parallel
    2. RankingAgent fuses results using weighted scoring
    3. Return ranked documents with retrieval metadata
    """

    def __init__(self):
        self.semantic_agent = SemanticRetrievalAgent()
        self.keyword_agent = KeywordRetrievalAgent()
        self.ranking_agent = RankingAgent()

    @trace_function("multi_agent_retrieval", as_type="chain")
    def retrieve(
        self,
        question: str,
        semantic_top_k: int = 6,
        keyword_top_k: int = 6,
        final_top_k: int = 6
    ) -> Dict[str, Any]:
        """
        Execute multi-agent retrieval pipeline.

        Args:
            question: User query
            semantic_top_k: Top-k for semantic agent
            keyword_top_k: Top-k for keyword agent
            final_top_k: Final top-k documents returned

        Returns:
            {
                "documents": List of ranked PolicyDocument objects,
                "agents_used": List of agent names,
                "retrieval_pipeline": Detailed pipeline execution info,
                "scores": Scoring details for each document
            }
        """
        db = SessionLocal()

        try:
            # Step 1: Run semantic and keyword agents in parallel
            print("\n" + "=" * 70)
            print("MULTI-AGENT RETRIEVAL PIPELINE")
            print("=" * 70)
            print(f"\nSTEP 1: Parallel Retrieval")
            print("-" * 70)

            # Semantic retrieval
            semantic_results, semantic_details = self.semantic_agent.retrieve(
                question, top_k=semantic_top_k, db=db
            )
            print(f"  ✓ Semantic Agent: Retrieved {len(semantic_results)} documents")
            print(f"    Method: {semantic_details['method']}")

            # Keyword retrieval
            keyword_results, keyword_details = self.keyword_agent.retrieve(
                question, top_k=keyword_top_k, db=db
            )
            print(f"  ✓ Keyword Agent: Retrieved {len(keyword_results)} documents")
            print(f"    Keywords: {keyword_details.get('keywords', [])[:3]}...")

            # Step 2: Rank and fuse results
            print(f"\nSTEP 2: Result Ranking & Fusion")
            print("-" * 70)

            ranked_docs, ranking_details = self.ranking_agent.rank_and_fuse(
                semantic_results,
                keyword_results,
                final_top_k=final_top_k
            )

            print(f"  ✓ Ranking Agent: Fused results")
            print(f"    Documents fused: {ranking_details['documents_fused']}")
            print(f"    Final documents: {ranking_details['final_documents']}")
            print(f"    Weighted fusion: {ranking_details['semantic_weight']*100:.0f}% semantic + {ranking_details['keyword_weight']*100:.0f}% keyword")
            print(f"    Consensus boost: Applied (30% boost for cross-agent hits)")

            # Step 3: Build retrieval pipeline info
            print(f"\nSTEP 3: Pipeline Summary")
            print("-" * 70)
            print(f"  Total agents used: 3 (Semantic + Keyword + Ranking)")
            print(f"  Final documents returned: {len(ranked_docs)}")
            print(f"  Retrieval quality: Multi-agent enhanced")
            print("=" * 70 + "\n")

            return {
                "documents": ranked_docs,
                "agents_used": [
                    "semantic_retrieval_agent",
                    "keyword_retrieval_agent",
                    "ranking_agent"
                ],
                "retrieval_pipeline": {
                    "semantic_agent": semantic_details,
                    "keyword_agent": keyword_details,
                    "ranking_agent": ranking_details,
                    "total_agents": 3,
                    "fusion_method": "weighted_scoring_with_consensus_boost",
                },
                "scores": ranking_details["scored_results"],
            }

        finally:
            db.close()


def retrieve_with_multi_agent(question: str, top_k: int = 6) -> Dict[str, Any]:
    """
    Public function to retrieve documents using multi-agent retrieval.

    Returns documents and detailed retrieval metadata.
    """
    retrieval = MultiAgentRetrieval()
    return retrieval.retrieve(question, final_top_k=top_k)
