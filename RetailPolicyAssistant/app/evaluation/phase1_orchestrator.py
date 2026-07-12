"""Phase 1 Evaluation Orchestrator - coordinates latency, TSR, and SQL correctness metrics."""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

from app.evaluation.config import get_evaluation_config, is_metric_enabled, get_metric_status
from app.evaluation.latency_breakdown import evaluate_latency, LatencyBreakdown
from app.evaluation.tsr import record_query_success, evaluate_query_success
from app.evaluation.sql_correctness import validate_sql, SQLCorrectnessResult
from app.observability.logger import AgentLogger
from app.core.percentile_tracker import add_latency_sample, get_all_percentiles


@dataclass
class Phase1EvaluationResult:
    """Result of Phase 1 evaluation (latency, TSR, SQL correctness)."""

    query_id: Optional[str] = None
    timestamp: str = ""

    # Latency metrics
    latency: Optional[LatencyBreakdown] = None
    latency_status: str = "good"

    # Percentile metrics (Phase 3.1)
    percentiles: Optional[Dict[str, Any]] = None

    # TSR metric
    success: bool = False
    tsr_current: float = 0.0
    tsr_status: str = "good"

    # SQL Correctness (if SQL route)
    sql_correctness: Optional[SQLCorrectnessResult] = None
    sql_status: str = "good"

    # Metadata
    errors: list = None

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
            "phase": 1,
        }

        if self.latency:
            result["latency"] = self.latency.to_dict()
            result["latency_status"] = self.latency_status

        # Phase 3.1: Include percentile metrics
        if self.percentiles:
            result["percentiles"] = self.percentiles

        result["success"] = self.success
        result["tsr_current"] = round(self.tsr_current, 4)
        result["tsr_status"] = self.tsr_status

        if self.sql_correctness:
            result["sql_correctness"] = self.sql_correctness.to_dict()
            result["sql_status"] = self.sql_status

        if self.errors:
            result["errors"] = self.errors

        return result


class Phase1Evaluator:
    """Evaluator for Phase 1 metrics: latency, TSR, SQL correctness."""

    def __init__(self):
        self.config = get_evaluation_config()
        self.logger = AgentLogger()

    async def evaluate_response(
        self,
        response: dict,
        query: str = "",
        route: str = "",
        retrieval_ms: Optional[float] = None,
        generation_ms: Optional[float] = None,
        sql_ms: Optional[float] = None,
        sql_query: Optional[str] = None,
        sql_execution_succeeded: bool = True,
        sql_error: Optional[str] = None,
        total_latency_ms: float = 0.0,
    ) -> Phase1EvaluationResult:
        """Evaluate response using Phase 1 metrics (sync evaluation, no LLM).

        Args:
            response: Orchestrator response dict
            query: Original user query
            route: Query route (rag/sql/hybrid)
            retrieval_ms: Retrieval time (optional)
            generation_ms: LLM generation time (optional)
            sql_ms: SQL execution time (optional)
            sql_query: Generated SQL query (if SQL route)
            sql_execution_succeeded: Whether SQL executed successfully
            sql_error: SQL error message if any
            total_latency_ms: Total request latency

        Returns:
            Phase1EvaluationResult with all Phase 1 metrics
        """
        start_time = time.time()
        result = Phase1EvaluationResult()
        result.timestamp = datetime.utcnow().isoformat()

        try:
            # 1. Evaluate Latency (always enabled)
            if is_metric_enabled("latency"):
                result.latency = evaluate_latency(
                    total_ms=total_latency_ms,
                    retrieval_ms=retrieval_ms,
                    generation_ms=generation_ms,
                    sql_ms=sql_ms,
                )
                result.latency_status = get_metric_status("latency_ms", total_latency_ms)

                # Phase 3.1: Track percentiles for SLO compliance
                add_latency_sample(total_latency_ms, route=route)
                result.percentiles = get_all_percentiles(slo_target_ms=2000.0)

            # 2. Evaluate TSR (query success/failure)
            if is_metric_enabled("tsr"):
                success = evaluate_query_success(response, escalated=response.get("escalate", False))
                record_query_success(success)
                result.success = success

                from app.evaluation.tsr import get_tsr_calculator
                calc = get_tsr_calculator()
                result.tsr_current = calc.get_rolling_tsr()
                result.tsr_status = get_metric_status("tsr", result.tsr_current)

            # 3. Evaluate SQL Correctness (if SQL route)
            if is_metric_enabled("sql_correctness") and route == "sql" and sql_query:
                result.sql_correctness = validate_sql(
                    query=sql_query,
                    execution_succeeded=sql_execution_succeeded,
                    execution_error=sql_error,
                )
                result.sql_status = get_metric_status(
                    "sql_correctness",
                    result.sql_correctness.confidence
                )

                if not result.sql_correctness.is_correct:
                    result.errors.extend(result.sql_correctness.issues)

        except Exception as e:
            result.errors.append(f"Evaluation error: {str(e)}")
            self.logger.log("evaluation_error", {"phase": 1, "error": str(e)})

        # Log evaluation timing
        eval_time_ms = (time.time() - start_time) * 1000
        self.logger.log("phase1_evaluation_complete", {
            "latency_ms": total_latency_ms,
            "eval_time_ms": eval_time_ms,
            "success": result.success,
        })

        return result

    def should_run_async(self) -> bool:
        """Whether Phase 1 evaluation should run asynchronously.

        Phase 1 is lightweight, so we can choose to run it sync or async
        depending on configuration.

        Returns:
            True if async evaluation is enabled, False for sync
        """
        return self.config.enable_background_evaluation


# Global singleton
_phase1_evaluator: Optional[Phase1Evaluator] = None


def get_phase1_evaluator() -> Phase1Evaluator:
    """Get the global Phase 1 evaluator instance."""
    global _phase1_evaluator
    if _phase1_evaluator is None:
        _phase1_evaluator = Phase1Evaluator()
    return _phase1_evaluator


async def evaluate_phase1(
    response: dict,
    query: str = "",
    route: str = "",
    retrieval_ms: Optional[float] = None,
    generation_ms: Optional[float] = None,
    sql_ms: Optional[float] = None,
    sql_query: Optional[str] = None,
    sql_execution_succeeded: bool = True,
    sql_error: Optional[str] = None,
    total_latency_ms: float = 0.0,
) -> Phase1EvaluationResult:
    """Evaluate a response using Phase 1 metrics.

    This is the main entry point for Phase 1 evaluation.

    Args:
        response: Orchestrator response dict
        query: Original user query
        route: Query route (rag/sql/hybrid)
        retrieval_ms: Retrieval time (optional)
        generation_ms: LLM generation time (optional)
        sql_ms: SQL execution time (optional)
        sql_query: Generated SQL query (if SQL route)
        sql_execution_succeeded: Whether SQL executed successfully
        sql_error: SQL error message if any
        total_latency_ms: Total request latency

    Returns:
        Phase1EvaluationResult
    """
    evaluator = get_phase1_evaluator()
    return await evaluator.evaluate_response(
        response=response,
        query=query,
        route=route,
        retrieval_ms=retrieval_ms,
        generation_ms=generation_ms,
        sql_ms=sql_ms,
        sql_query=sql_query,
        sql_execution_succeeded=sql_execution_succeeded,
        sql_error=sql_error,
        total_latency_ms=total_latency_ms,
    )
