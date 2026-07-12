"""LangFuse score and evaluation tracing."""

from typing import Optional, Dict, Any
import json


class ScoreTracer:
    """Traces confidence scores and evaluation metrics to LangFuse."""

    @staticmethod
    def log_score(
        score_name: str,
        score_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a score to LangFuse trace.

        Args:
            score_name: Name of the score (e.g., "confidence", "accuracy", "route_correctness")
            score_value: Score value (0.0-1.0)
            metadata: Additional metadata to attach to the score
        """
        try:
            # Validate score value
            if not (0.0 <= score_value <= 1.0):
                print(f"[WARNING] Invalid score value: {score_value}, must be 0.0-1.0, skipping Langfuse logging")
                return

            # Create metadata payload
            meta_dict = metadata or {}

            # Validate metadata is JSON-serializable
            try:
                meta_str = json.dumps(meta_dict) if meta_dict else "{}"
            except (TypeError, ValueError) as e:
                print(f"[WARNING] Metadata not JSON-serializable: {e}, skipping Langfuse logging")
                return

            # Log to console for visibility
            print(f"[LANGFUSE SCORE] name={score_name} value={score_value:.2f} metadata={meta_str}")

            # Send to LangFuse client if available
            from app.observability.langfuse_tracer import get_tracer

            tracer = get_tracer()
            if tracer.is_enabled() and tracer.client:
                # Try to get current trace context from Langfuse
                trace_id = None
                observation_id = None

                try:
                    from langfuse.context import get_current_trace_id, get_current_observation_id
                    trace_id = get_current_trace_id()
                    observation_id = get_current_observation_id()
                except (ImportError, AttributeError):
                    # Langfuse version doesn't have context module
                    pass

                # Skip if no trace context available
                if not trace_id:
                    print(f"[INFO] No trace context available, logging to console only")
                    return

                # Log score to Langfuse using create_score() method
                try:
                    tracer.client.create_score(
                        name=score_name,
                        value=score_value,
                        data_type="NUMERIC",
                        comment=meta_str,
                        trace_id=trace_id,
                        observation_id=observation_id
                    )
                    ctx_info = ""
                    if trace_id:
                        ctx_info = f" (trace_id={trace_id[:8]}...)"
                    print(f"[LANGFUSE] Score '{score_name}' logged to Langfuse{ctx_info}")
                except TypeError:
                    # Older Langfuse SDK without all params
                    try:
                        tracer.client.create_score(
                            name=score_name,
                            value=score_value,
                            data_type="NUMERIC",
                            comment=meta_str
                        )
                        print(f"[LANGFUSE] Score '{score_name}' logged to Langfuse")
                    except Exception as inner_e:
                        print(f"[WARNING] Failed to create score: {inner_e}")
            else:
                print(f"[INFO] Langfuse not enabled, score logged to console only")

        except Exception as e:
            # Don't fail query if score tracing fails
            print(f"[WARNING] Score tracing failed (query will continue): {e}")

    @staticmethod
    def log_evaluation_result(
        result_id: str,
        evaluation_metrics: Dict[str, float],
        test_name: str
    ):
        """
        Log evaluation results to LangFuse.

        Args:
            result_id: Unique result ID
            evaluation_metrics: Dict of metric_name -> score
            test_name: Name of test run
        """
        try:
            # Format metrics for logging
            metrics_str = json.dumps(evaluation_metrics, indent=2)

            print(f"[LANGFUSE EVAL] test_name={test_name} result_id={result_id}")
            print(f"Metrics:\n{metrics_str}")

            # Log each metric individually
            for metric_name, metric_value in evaluation_metrics.items():
                print(f"  - {metric_name}: {metric_value:.4f}")

            # Send to LangFuse if available
            from app.observability.langfuse_tracer import get_tracer

            tracer = get_tracer()
            if tracer.is_enabled() and tracer.client:
                # Log each metric as a score to Langfuse
                for metric_name, metric_value in evaluation_metrics.items():
                    try:
                        tracer.client.create_score(
                            name=metric_name,
                            value=metric_value,
                            data_type="NUMERIC",
                            comment=f"Evaluation: {test_name}, Result: {result_id}"
                        )
                    except Exception as e:
                        print(f"[WARNING] Failed to log metric {metric_name}: {e}")
                print(f"[LANGFUSE] {len(evaluation_metrics)} evaluation metrics logged to Langfuse")
            else:
                print(f"[INFO] Langfuse not enabled, metrics logged to console only")

        except Exception as e:
            print(f"[WARNING] Evaluation tracing failed (metrics will be logged): {e}")

    @staticmethod
    def log_query_execution(
        query: str,
        route: str,
        confidence: float,
        risk_level: str,
        latency_ms: float,
        user_id: str = "anonymous"
    ):
        """
        Log a complete query execution with all scores.

        Args:
            query: The user query
            route: Route decision (rag, sql, hybrid)
            confidence: Confidence score 0.0-1.0
            risk_level: Risk level (low, medium, high)
            latency_ms: Query latency in milliseconds
            user_id: User who made the query
        """
        ScoreTracer.log_score(
            score_name="query_execution",
            score_value=confidence,
            metadata={
                "route": route,
                "risk_level": risk_level,
                "latency_ms": round(latency_ms, 2),
                "user_id": user_id,
                "query_preview": query[:100] if query else "",
            }
        )

    @staticmethod
    def log_retrieval_metrics(
        context_precision: float,
        context_recall: float,
        query_id: Optional[str] = None,
        doc_count: int = 0,
        retrieval_latency_ms: float = 0.0,
        retrieval_method: str = "unknown",
        route: str = "rag"
    ):
        """Log Phase 2 retrieval quality metrics to Langfuse.

        Args:
            context_precision: Context precision score (0.0-1.0)
            context_recall: Context recall score (0.0-1.0)
            query_id: Optional query ID for correlation
            doc_count: Number of documents retrieved
            retrieval_latency_ms: Retrieval time in milliseconds
            retrieval_method: Method used (semantic, keyword, multi_agent)
            route: Query route (rag, sql, hybrid)
        """
        # Log precision score
        ScoreTracer.log_score(
            score_name="context_precision",
            score_value=context_precision,
            metadata={
                "query_id": query_id,
                "doc_count": doc_count,
                "retrieval_method": retrieval_method,
                "route": route,
                "retrieval_latency_ms": round(retrieval_latency_ms, 2),
            }
        )

        # Log recall score
        ScoreTracer.log_score(
            score_name="context_recall",
            score_value=context_recall,
            metadata={
                "query_id": query_id,
                "doc_count": doc_count,
                "retrieval_method": retrieval_method,
                "route": route,
                "retrieval_latency_ms": round(retrieval_latency_ms, 2),
            }
        )
