"""Phase 2 Retrieval Quality Metrics - Context Precision and Context Recall."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from collections import deque
from datetime import datetime


@dataclass
class RetrievalMetrics:
    """Result of retrieval quality evaluation (context precision and recall)."""

    query_id: Optional[str] = None
    timestamp: str = ""

    # Retrieval metrics
    context_precision: float = 0.0
    context_recall: float = 0.0
    precision_status: str = "good"  # good/warning/critical
    recall_status: str = "good"

    # Metadata
    retrieved_doc_count: int = 0
    retrieval_latency_ms: float = 0.0
    retrieval_method: str = "unknown"  # semantic, keyword, multi_agent
    route: str = "rag"  # rag, sql, hybrid
    query_text: Optional[str] = None

    # Supporting metrics
    avg_chunk_relevance: float = 0.0
    retrieval_diversity_score: float = 0.0
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize defaults."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for response/logging."""
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "phase": 2,
            "context_precision": round(self.context_precision, 4),
            "context_recall": round(self.context_recall, 4),
            "precision_status": self.precision_status,
            "recall_status": self.recall_status,
            "retrieved_doc_count": self.retrieved_doc_count,
            "retrieval_latency_ms": round(self.retrieval_latency_ms, 2),
            "retrieval_method": self.retrieval_method,
            "route": self.route,
            "avg_chunk_relevance": round(self.avg_chunk_relevance, 4),
            "retrieval_diversity_score": round(self.retrieval_diversity_score, 4),
            "errors": self.errors,
        }


class RetrievalMetricCalculator:
    """Calculates rolling statistics for retrieval metrics."""

    def __init__(self, window_size: int = 1000):
        """Initialize calculator with rolling window.

        Args:
            window_size: Number of metrics to keep in rolling window
        """
        self.window_size = window_size
        self.history: deque = deque(maxlen=window_size)
        self.global_count = 0
        self.global_precision_sum = 0.0
        self.global_recall_sum = 0.0

    def record_metrics(self, metrics: RetrievalMetrics) -> None:
        """Record a set of retrieval metrics.

        Args:
            metrics: RetrievalMetrics instance to record
        """
        self.history.append(metrics)
        self.global_count += 1
        self.global_precision_sum += metrics.context_precision
        self.global_recall_sum += metrics.context_recall

    def get_rolling_precision(self) -> float:
        """Get average precision for rolling window.

        Returns:
            Average context precision (0.0-1.0) or 0.0 if no data
        """
        if not self.history:
            return 0.0
        return sum(m.context_precision for m in self.history) / len(self.history)

    def get_rolling_recall(self) -> float:
        """Get average recall for rolling window.

        Returns:
            Average context recall (0.0-1.0) or 0.0 if no data
        """
        if not self.history:
            return 0.0
        return sum(m.context_recall for m in self.history) / len(self.history)

    def get_global_precision(self) -> float:
        """Get average precision across all recorded metrics.

        Returns:
            Average context precision or 0.0 if no data
        """
        if self.global_count == 0:
            return 0.0
        return self.global_precision_sum / self.global_count

    def get_global_recall(self) -> float:
        """Get average recall across all recorded metrics.

        Returns:
            Average context recall or 0.0 if no data
        """
        if self.global_count == 0:
            return 0.0
        return self.global_recall_sum / self.global_count

    def get_rolling_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for rolling window.

        Returns:
            Dictionary with min, max, avg, median, p95, p99 for both metrics
        """
        if not self.history:
            return {
                "count": 0,
                "precision": {"min": 0.0, "max": 0.0, "avg": 0.0, "median": 0.0},
                "recall": {"min": 0.0, "max": 0.0, "avg": 0.0, "median": 0.0},
            }

        precisions = [m.context_precision for m in self.history]
        recalls = [m.context_recall for m in self.history]

        # Sort for percentile calculations
        precisions_sorted = sorted(precisions)
        recalls_sorted = sorted(recalls)
        count = len(self.history)

        def get_percentile(sorted_list, p):
            idx = int((p / 100.0) * len(sorted_list))
            return sorted_list[min(idx, len(sorted_list) - 1)]

        return {
            "count": count,
            "precision": {
                "min": min(precisions),
                "max": max(precisions),
                "avg": sum(precisions) / count,
                "median": get_percentile(precisions_sorted, 50),
                "p95": get_percentile(precisions_sorted, 95),
                "p99": get_percentile(precisions_sorted, 99),
            },
            "recall": {
                "min": min(recalls),
                "max": max(recalls),
                "avg": sum(recalls) / count,
                "median": get_percentile(recalls_sorted, 50),
                "p95": get_percentile(recalls_sorted, 95),
                "p99": get_percentile(recalls_sorted, 99),
            },
        }

    def get_global_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics across all metrics.

        Returns:
            Dictionary with global averages
        """
        return {
            "total_evals": self.global_count,
            "avg_precision": round(self.get_global_precision(), 4),
            "avg_recall": round(self.get_global_recall(), 4),
        }


# Global singleton instance
_calculator_instance: Optional[RetrievalMetricCalculator] = None


def get_retrieval_metrics_calculator() -> RetrievalMetricCalculator:
    """Get or create global retrieval metrics calculator.

    Returns:
        Global RetrievalMetricCalculator instance
    """
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = RetrievalMetricCalculator()
    return _calculator_instance
