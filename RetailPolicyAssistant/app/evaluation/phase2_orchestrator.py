"""Phase 2 Evaluation Orchestrator - Coordinates retrieval quality metrics."""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.evaluation.config import get_evaluation_config, is_metric_enabled, get_metric_status
from app.evaluation.retrieval_metrics import (
    RetrievalMetrics,
    get_retrieval_metrics_calculator,
)
from app.evaluation.context_precision import ContextPrecisionEvaluator
from app.evaluation.context_recall import ContextRecallEvaluator
from app.observability.logger import AgentLogger


@dataclass
class Phase2EvaluationResult:
    """Result of Phase 2 evaluation (retrieval quality metrics)."""

    query_id: Optional[str] = None
    timestamp: str = ""

    # Retrieval metrics
    retrieval_metrics: Optional[RetrievalMetrics] = None

    # Metadata
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for response/logging."""
        result = {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "phase": 2,
        }

        if self.retrieval_metrics:
            result["retrieval_metrics"] = self.retrieval_metrics.to_dict()

        if self.errors:
            result["errors"] = self.errors

        return result


class Phase2Evaluator:
    """Evaluator for Phase 2 metrics: context precision and recall."""

    def __init__(self):
        self.config = get_evaluation_config()
        self.logger = AgentLogger()
        self.precision_evaluator = ContextPrecisionEvaluator()
        self.recall_evaluator = ContextRecallEvaluator()

    async def evaluate_retrieval(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        route: str = "rag",
        retrieval_latency_ms: float = 0.0,
        retrieval_method: str = "unknown",
    ) -> Phase2EvaluationResult:
        """Evaluate retrieval quality metrics.

        Args:
            query: Original user query
            retrieved_chunks: List of retrieved document chunks
            route: Query route (rag, sql, hybrid)
            retrieval_latency_ms: Time spent on retrieval
            retrieval_method: Method used (semantic, keyword, multi_agent)

        Returns:
            Phase2EvaluationResult with context precision and recall scores
        """
        start_time = time.time()
        result = Phase2EvaluationResult()
        result.timestamp = datetime.utcnow().isoformat()

        try:
            metrics = RetrievalMetrics()
            metrics.query_text = query
            metrics.route = route
            metrics.retrieval_latency_ms = retrieval_latency_ms
            metrics.retrieval_method = retrieval_method
            metrics.retrieved_doc_count = len(retrieved_chunks)

            # 1. Evaluate Context Precision (always enabled if Phase 2 enabled)
            if is_metric_enabled("context_precision"):
                try:
                    precision_score = self.precision_evaluator.evaluate_precision(
                        query=query,
                        retrieved_chunks=retrieved_chunks,
                        route=route,
                    )
                    metrics.context_precision = precision_score
                    metrics.precision_status = get_metric_status(
                        "context_precision",
                        precision_score,
                    )
                    self.logger.log("context_precision_evaluated", {
                        "score": precision_score,
                        "status": metrics.precision_status,
                        "doc_count": len(retrieved_chunks),
                    })
                except Exception as e:
                    result.errors.append(f"Context precision evaluation error: {str(e)}")
                    self.logger.log("context_precision_error", {"error": str(e)})

            # 2. Evaluate Context Recall (always enabled if Phase 2 enabled)
            if is_metric_enabled("context_recall"):
                try:
                    recall_score = self.recall_evaluator.evaluate_recall(
                        query=query,
                        retrieved_chunks=retrieved_chunks,
                        route=route,
                    )
                    metrics.context_recall = recall_score
                    metrics.recall_status = get_metric_status(
                        "context_recall",
                        recall_score,
                    )
                    self.logger.log("context_recall_evaluated", {
                        "score": recall_score,
                        "status": metrics.recall_status,
                        "doc_count": len(retrieved_chunks),
                    })
                except Exception as e:
                    result.errors.append(f"Context recall evaluation error: {str(e)}")
                    self.logger.log("context_recall_error", {"error": str(e)})

            # 3. Calculate additional metrics
            try:
                metrics.avg_chunk_relevance = self._calculate_avg_chunk_relevance(
                    retrieved_chunks
                )
                metrics.retrieval_diversity_score = self._calculate_retrieval_diversity(
                    retrieved_chunks
                )
            except Exception as e:
                self.logger.log("supplemental_metrics_error", {"error": str(e)})

            # Record in global calculator
            calc = get_retrieval_metrics_calculator()
            calc.record_metrics(metrics)

            result.retrieval_metrics = metrics

            # Log to Langfuse via ScoreTracer
            from app.observability.score_tracer import ScoreTracer
            ScoreTracer.log_retrieval_metrics(
                context_precision=metrics.context_precision,
                context_recall=metrics.context_recall,
                query_id=metrics.query_id,
                doc_count=metrics.retrieved_doc_count,
                retrieval_latency_ms=metrics.retrieval_latency_ms,
                retrieval_method=metrics.retrieval_method,
                route=metrics.route,
            )

            # Log evaluation duration
            eval_time_ms = (time.time() - start_time) * 1000
            self.logger.log("phase2_evaluation_complete", {
                "duration_ms": eval_time_ms,
                "precision": metrics.context_precision,
                "recall": metrics.context_recall,
            })

        except Exception as e:
            result.errors.append(f"Phase 2 evaluation error: {str(e)}")
            self.logger.log("phase2_evaluation_error", {"error": str(e)})

        return result

    def _calculate_avg_chunk_relevance(
        self,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> float:
        """Calculate average relevance score across chunks.

        Args:
            retrieved_chunks: Retrieved document chunks

        Returns:
            Average relevance score 0.0-1.0
        """
        if not retrieved_chunks:
            return 0.0

        relevance_scores = []
        for chunk in retrieved_chunks:
            score = chunk.get("retrieval_score") or chunk.get("score") or 0.0
            if isinstance(score, (int, float)):
                relevance_scores.append(min(1.0, max(0.0, score)))

        if not relevance_scores:
            return 0.5  # Default if no scores available

        return sum(relevance_scores) / len(relevance_scores)

    def _calculate_retrieval_diversity(
        self,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> float:
        """Calculate diversity of retrieved documents (sections and sources).

        Args:
            retrieved_chunks: Retrieved document chunks

        Returns:
            Diversity score 0.0-1.0 (higher = more diverse)
        """
        if len(retrieved_chunks) < 2:
            return 0.5

        # Track unique values
        unique_sections = set()
        unique_documents = set()

        for chunk in retrieved_chunks:
            section = chunk.get("section") or ""
            if section:
                unique_sections.add(section)

            doc = chunk.get("document") or chunk.get("document_name") or ""
            if doc:
                unique_documents.add(doc)

        # Diversity score combines section and document diversity
        section_diversity = len(unique_sections) / max(len(retrieved_chunks), 1)
        doc_diversity = len(unique_documents) / max(len(retrieved_chunks), 1)

        # Weight: sections are more important (more sources = better)
        diversity = (section_diversity * 0.6) + (doc_diversity * 0.4)
        return min(1.0, max(0.0, diversity))


def evaluate_phase2_sync(
    query: str,
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
    route: str = "rag",
    retrieval_latency_ms: float = 0.0,
    retrieval_method: str = "unknown",
) -> Optional[dict]:
    """Synchronous Phase 2 evaluation to attach metrics to response immediately.

    Returns dict with precision/recall for immediate response inclusion.

    Args:
        query: Original user query
        retrieved_chunks: Retrieved document chunks
        route: Query route
        retrieval_latency_ms: Retrieval time
        retrieval_method: Method used

    Returns:
        Dict with precision/recall or None
    """
    config = get_evaluation_config()
    if not (config.enable_context_precision or config.enable_context_recall):
        return None

    try:
        evaluator = Phase2Evaluator()
        logger = AgentLogger()

        if retrieved_chunks is None:
            retrieved_chunks = []

        metrics_dict = {}

        if is_metric_enabled("context_precision"):
            try:
                precision_score = evaluator.precision_evaluator.evaluate_precision(
                    query=query,
                    retrieved_chunks=retrieved_chunks,
                    route=route,
                )
                metrics_dict["precision"] = round(precision_score, 4)
            except Exception as e:
                logger.log("precision_sync_error", {"error": str(e)})

        if is_metric_enabled("context_recall"):
            try:
                recall_score = evaluator.recall_evaluator.evaluate_recall(
                    query=query,
                    retrieved_chunks=retrieved_chunks,
                    route=route,
                )
                metrics_dict["recall"] = round(recall_score, 4)
            except Exception as e:
                logger.log("recall_sync_error", {"error": str(e)})

        return metrics_dict if metrics_dict else None

    except Exception as e:
        logger = AgentLogger()
        logger.log("phase2_sync_evaluation_error", {"error": str(e)})
        return None


async def evaluate_phase2(
    response: dict,
    query: str,
    route: str = "rag",
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
    retrieval_latency_ms: float = 0.0,
    retrieval_method: str = "unknown",
) -> Optional[Phase2EvaluationResult]:
    """Top-level async function to evaluate Phase 2 metrics.

    This is called asynchronously from the orchestrator - non-blocking.

    Args:
        response: Orchestrator response dict
        query: Original user query
        route: Query route (rag, sql, hybrid)
        retrieved_chunks: Retrieved document chunks
        retrieval_latency_ms: Time spent on retrieval
        retrieval_method: Retrieval method used

    Returns:
        Phase2EvaluationResult or None if evaluation skipped
    """
    # Check if Phase 2 evaluation is enabled
    config = get_evaluation_config()
    if not (config.enable_context_precision or config.enable_context_recall):
        return None

    try:
        evaluator = Phase2Evaluator()

        # Handle missing chunks
        if retrieved_chunks is None:
            retrieved_chunks = []
            # Try to extract from response
            if "sources" in response:
                retrieved_chunks = response["sources"]

        result = await evaluator.evaluate_retrieval(
            query=query,
            retrieved_chunks=retrieved_chunks,
            route=route,
            retrieval_latency_ms=retrieval_latency_ms,
            retrieval_method=retrieval_method,
        )

        return result

    except Exception as e:
        logger = AgentLogger()
        logger.log("phase2_async_evaluation_error", {"error": str(e)})
        return None
