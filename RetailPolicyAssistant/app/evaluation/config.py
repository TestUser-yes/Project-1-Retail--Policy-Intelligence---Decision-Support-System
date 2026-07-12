"""Evaluation framework configuration and feature flags."""

import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class EvaluationConfig:
    """Configuration for evaluation metrics with feature flags."""

    # ===== PHASE 1: OPERATIONAL METRICS =====
    # Lightweight metrics with no LLM evaluation
    enable_latency: bool = True  # Track latency breakdown (always enabled)
    enable_tsr: bool = True  # Task Success Rate (always enabled)
    enable_sql_correctness: bool = True  # SQL correctness validation (always enabled)

    # ===== PHASE 2: RETRIEVAL QUALITY =====
    # RAGAS-based metrics for RAG pipeline evaluation
    enable_context_precision: bool = True
    enable_context_recall: bool = True

    # ===== PHASE 3: RESPONSE QUALITY =====
    # RAGAS-based metrics for answer quality
    enable_answer_relevance: bool = True
    enable_faithfulness: bool = True

    # ===== PHASE 4: ACCURACY =====
    # LLM-as-Judge (optional, can be expensive)
    enable_accuracy: bool = False

    # ===== EXECUTION MODEL =====
    enable_background_evaluation: bool = True  # Run heavy metrics async
    evaluation_timeout_seconds: float = 30.0  # Max time for evaluation
    max_concurrent_evaluations: int = 5  # Async task concurrency limit

    # ===== RAGAS CONFIGURATION =====
    ragas_batch_size: int = 10
    ragas_timeout_seconds: float = 20.0

    # ===== LLM JUDGE CONFIGURATION =====
    llm_judge_model: str = "gpt-4o-mini"  # Model for LLM-as-judge
    llm_judge_timeout_seconds: float = 15.0

    # ===== LANGFUSE INTEGRATION =====
    enable_langfuse_logging: bool = True  # Log all metrics to Langfuse
    log_evaluation_details: bool = False  # Log detailed eval results (verbose)

    # ===== DATABASE =====
    persist_evaluation_results: bool = True  # Store in evaluation_runs table
    persist_query_metrics: bool = True  # Store in ai_queries table


def load_evaluation_config() -> EvaluationConfig:
    """Load evaluation configuration from environment variables.

    Environment variables follow pattern: EVAL_* or ENABLE_*

    Examples:
        EVAL_ENABLE_LATENCY=true
        EVAL_ENABLE_RAGAS=true
        EVAL_ENABLE_ACCURACY=false
        EVAL_BACKGROUND_ENABLED=true
        EVAL_TIMEOUT_SECONDS=30
    """
    config = EvaluationConfig()

    # ===== PHASE 1: OPERATIONAL METRICS =====
    config.enable_latency = _parse_bool(
        os.getenv("EVAL_ENABLE_LATENCY", os.getenv("ENABLE_LATENCY", "true"))
    )
    config.enable_tsr = _parse_bool(
        os.getenv("EVAL_ENABLE_TSR", os.getenv("ENABLE_TSR", "true"))
    )
    config.enable_sql_correctness = _parse_bool(
        os.getenv("EVAL_ENABLE_SQL_CORRECTNESS", os.getenv("ENABLE_SQL_CORRECTNESS", "true"))
    )

    # ===== PHASE 2: RETRIEVAL QUALITY =====
    config.enable_context_precision = _parse_bool(
        os.getenv("EVAL_ENABLE_CONTEXT_PRECISION", os.getenv("ENABLE_CONTEXT_PRECISION", "true"))
    )
    config.enable_context_recall = _parse_bool(
        os.getenv("EVAL_ENABLE_CONTEXT_RECALL", os.getenv("ENABLE_CONTEXT_RECALL", "true"))
    )

    # ===== PHASE 3: RESPONSE QUALITY =====
    config.enable_answer_relevance = _parse_bool(
        os.getenv("EVAL_ENABLE_ANSWER_RELEVANCE", os.getenv("ENABLE_ANSWER_RELEVANCE", "true"))
    )
    config.enable_faithfulness = _parse_bool(
        os.getenv("EVAL_ENABLE_FAITHFULNESS", os.getenv("ENABLE_FAITHFULNESS", "true"))
    )

    # ===== PHASE 4: ACCURACY =====
    config.enable_accuracy = _parse_bool(
        os.getenv("EVAL_ENABLE_ACCURACY", os.getenv("ENABLE_ACCURACY", "false"))
    )

    # ===== EXECUTION MODEL =====
    config.enable_background_evaluation = _parse_bool(
        os.getenv("EVAL_BACKGROUND_ENABLED", os.getenv("ENABLE_BACKGROUND_EVALUATION", "true"))
    )
    config.evaluation_timeout_seconds = float(
        os.getenv("EVAL_TIMEOUT_SECONDS", "30.0")
    )
    config.max_concurrent_evaluations = int(
        os.getenv("EVAL_MAX_CONCURRENT", "5")
    )

    # ===== RAGAS CONFIGURATION =====
    config.ragas_batch_size = int(
        os.getenv("EVAL_RAGAS_BATCH_SIZE", "10")
    )
    config.ragas_timeout_seconds = float(
        os.getenv("EVAL_RAGAS_TIMEOUT_SECONDS", "20.0")
    )

    # ===== LLM JUDGE CONFIGURATION =====
    config.llm_judge_model = os.getenv("EVAL_LLM_JUDGE_MODEL", "gpt-4o-mini")
    config.llm_judge_timeout_seconds = float(
        os.getenv("EVAL_LLM_JUDGE_TIMEOUT_SECONDS", "15.0")
    )

    # ===== LANGFUSE INTEGRATION =====
    config.enable_langfuse_logging = _parse_bool(
        os.getenv("EVAL_LANGFUSE_ENABLED", "true")
    )
    config.log_evaluation_details = _parse_bool(
        os.getenv("EVAL_LOG_DETAILS", "false")
    )

    # ===== DATABASE =====
    config.persist_evaluation_results = _parse_bool(
        os.getenv("EVAL_PERSIST_RESULTS", "true")
    )
    config.persist_query_metrics = _parse_bool(
        os.getenv("EVAL_PERSIST_QUERY_METRICS", "true")
    )

    return config


def _parse_bool(value: str) -> bool:
    """Parse environment variable to boolean.

    Accepts: true, True, TRUE, 1, yes, Yes, YES
    Rejects: false, False, FALSE, 0, no, No, NO
    """
    if not value:
        return False
    return value.lower() in ("true", "1", "yes", "on")


# Global singleton config
_config: EvaluationConfig | None = None


def get_evaluation_config() -> EvaluationConfig:
    """Get the global evaluation configuration (lazy loaded)."""
    global _config
    if _config is None:
        _config = load_evaluation_config()
    return _config


def reset_evaluation_config() -> None:
    """Reset global config (for testing)."""
    global _config
    _config = None


# ===== METRIC THRESHOLDS & TARGETS =====
# Used for determining Good/Warning/Critical status

METRIC_THRESHOLDS = {
    "latency_ms": {
        "good": 2000,  # <= 2s is good
        "warning": 3000,  # <= 3s is warning
        "critical": 5000,  # > 5s is critical
    },
    "tsr": {
        "good": 0.95,  # >= 95% is good
        "warning": 0.90,  # >= 90% is warning
        "critical": 0.90,  # < 90% is critical
    },
    "sql_correctness": {
        "good": 0.99,  # >= 99% is good
        "warning": 0.95,  # >= 95% is warning
        "critical": 0.95,  # < 95% is critical
    },
    "context_precision": {
        "good": 0.90,  # >= 90% is good
        "warning": 0.75,  # >= 75% is warning
        "critical": 0.75,  # < 75% is critical
    },
    "context_recall": {
        "good": 0.85,  # >= 85% is good
        "warning": 0.70,  # >= 70% is warning
        "critical": 0.70,  # < 70% is critical
    },
    "answer_relevance": {
        "good": 0.90,  # >= 90% is good
        "warning": 0.75,  # >= 75% is warning
        "critical": 0.75,  # < 75% is critical
    },
    "faithfulness": {
        "good": 0.92,  # >= 92% is good
        "warning": 0.80,  # >= 80% is warning
        "critical": 0.80,  # < 80% is critical
    },
    "accuracy": {
        "good": 0.95,  # >= 95% is good
        "warning": 0.85,  # >= 85% is warning
        "critical": 0.85,  # < 85% is critical
    },
}


def get_metric_status(metric_name: str, value: float) -> str:
    """Determine status (good/warning/critical) for a metric.

    Args:
        metric_name: Name of the metric (e.g., "faithfulness", "latency_ms")
        value: Metric value

    Returns:
        "good", "warning", or "critical"
    """
    thresholds = METRIC_THRESHOLDS.get(metric_name, {})
    if not thresholds:
        return "good"  # Default to good if metric not in thresholds

    # For metrics where higher is better (0-1 scale)
    if metric_name in ("tsr", "context_precision", "context_recall",
                       "answer_relevance", "faithfulness", "accuracy", "sql_correctness"):
        if value >= thresholds["good"]:
            return "good"
        elif value >= thresholds["warning"]:
            return "warning"
        else:
            return "critical"

    # For metrics where lower is better (latency)
    if metric_name == "latency_ms":
        if value <= thresholds["good"]:
            return "good"
        elif value <= thresholds["warning"]:
            return "warning"
        else:
            return "critical"

    return "good"  # Default


def is_metric_enabled(metric_name: str) -> bool:
    """Check if a specific metric is enabled.

    Args:
        metric_name: Name of the metric (e.g., "faithfulness", "latency")

    Returns:
        True if enabled, False otherwise
    """
    config = get_evaluation_config()

    # Phase 1: Operational Metrics (always on by default)
    if metric_name == "latency":
        return config.enable_latency
    elif metric_name == "tsr":
        return config.enable_tsr
    elif metric_name == "sql_correctness":
        return config.enable_sql_correctness

    # Phase 2: Retrieval Quality
    elif metric_name == "context_precision":
        return config.enable_context_precision
    elif metric_name == "context_recall":
        return config.enable_context_recall

    # Phase 3: Response Quality
    elif metric_name == "answer_relevance":
        return config.enable_answer_relevance
    elif metric_name == "faithfulness":
        return config.enable_faithfulness

    # Phase 4: Accuracy
    elif metric_name == "accuracy":
        return config.enable_accuracy

    return False
