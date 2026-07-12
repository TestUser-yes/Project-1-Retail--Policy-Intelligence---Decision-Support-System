"""Latency breakdown evaluation - tracks request latency at different pipeline stages."""

from dataclasses import dataclass, asdict
from typing import Optional, List
import statistics


@dataclass
class LatencyBreakdown:
    """Latency metrics broken down by pipeline stage."""

    total_ms: float  # Total request time
    retrieval_ms: Optional[float] = None  # Vector search + doc retrieval
    generation_ms: Optional[float] = None  # LLM generation time
    sql_ms: Optional[float] = None  # SQL execution time
    guardrails_ms: Optional[float] = None  # Guardrails validation
    orchestration_overhead_ms: Optional[float] = None  # Orchestrator logic

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = asdict(self)
        return {k: v for k, v in result.items() if v is not None}

    def __post_init__(self):
        """Validate latency values."""
        if self.total_ms < 0:
            raise ValueError("Total latency cannot be negative")
        if self.retrieval_ms is not None and self.retrieval_ms < 0:
            raise ValueError("Retrieval latency cannot be negative")
        if self.generation_ms is not None and self.generation_ms < 0:
            raise ValueError("Generation latency cannot be negative")
        if self.sql_ms is not None and self.sql_ms < 0:
            raise ValueError("SQL latency cannot be negative")


class LatencyMetricCalculator:
    """Calculate latency metrics and percentiles."""

    def __init__(self):
        self.latency_history: List[LatencyBreakdown] = []

    def record_latency(self, latency: LatencyBreakdown) -> None:
        """Record a latency measurement."""
        self.latency_history.append(latency)

    def get_percentile(self, percentile: float) -> Optional[float]:
        """Get total latency percentile (e.g., 0.95 for p95).

        Args:
            percentile: Percentile value (0.0-1.0)

        Returns:
            Total latency at that percentile, or None if no data
        """
        if not self.latency_history:
            return None

        total_latencies = [l.total_ms for l in self.latency_history]
        sorted_latencies = sorted(total_latencies)

        idx = int(percentile * (len(sorted_latencies) - 1))
        return sorted_latencies[idx]

    def get_average_breakdown(self) -> Optional[LatencyBreakdown]:
        """Get average latency breakdown across all measurements.

        Returns:
            LatencyBreakdown with average values, or None if no data
        """
        if not self.latency_history:
            return None

        avg_total = statistics.mean([l.total_ms for l in self.latency_history])

        # Calculate averages for optional fields if they have data
        retrieval_values = [l.retrieval_ms for l in self.latency_history if l.retrieval_ms is not None]
        avg_retrieval = statistics.mean(retrieval_values) if retrieval_values else None

        generation_values = [l.generation_ms for l in self.latency_history if l.generation_ms is not None]
        avg_generation = statistics.mean(generation_values) if generation_values else None

        sql_values = [l.sql_ms for l in self.latency_history if l.sql_ms is not None]
        avg_sql = statistics.mean(sql_values) if sql_values else None

        guardrails_values = [l.guardrails_ms for l in self.latency_history if l.guardrails_ms is not None]
        avg_guardrails = statistics.mean(guardrails_values) if guardrails_values else None

        orchestration_values = [l.orchestration_overhead_ms for l in self.latency_history if l.orchestration_overhead_ms is not None]
        avg_orchestration = statistics.mean(orchestration_values) if orchestration_values else None

        return LatencyBreakdown(
            total_ms=avg_total,
            retrieval_ms=avg_retrieval,
            generation_ms=avg_generation,
            sql_ms=avg_sql,
            guardrails_ms=avg_guardrails,
            orchestration_overhead_ms=avg_orchestration,
        )

    def get_summary(self) -> dict:
        """Get comprehensive latency summary.

        Returns:
            {
                "count": int,
                "total_ms": {
                    "min": float,
                    "max": float,
                    "avg": float,
                    "median": float,
                    "p50": float,
                    "p95": float,
                    "p99": float,
                },
                "breakdown": {
                    "retrieval_ms": {...},
                    "generation_ms": {...},
                    "sql_ms": {...},
                    ...
                }
            }
        """
        if not self.latency_history:
            return {"count": 0, "total_ms": {}}

        total_latencies = [l.total_ms for l in self.latency_history]
        sorted_latencies = sorted(total_latencies)

        summary = {
            "count": len(self.latency_history),
            "total_ms": {
                "min": min(total_latencies),
                "max": max(total_latencies),
                "avg": statistics.mean(total_latencies),
                "median": statistics.median(sorted_latencies),
                "p50": sorted_latencies[int(0.50 * (len(sorted_latencies) - 1))],
                "p95": sorted_latencies[int(0.95 * (len(sorted_latencies) - 1))] if len(sorted_latencies) > 1 else sorted_latencies[0],
                "p99": sorted_latencies[int(0.99 * (len(sorted_latencies) - 1))] if len(sorted_latencies) > 1 else sorted_latencies[0],
            }
        }

        # Add breakdown for optional fields
        breakdown = {}

        retrieval_values = [l.retrieval_ms for l in self.latency_history if l.retrieval_ms is not None]
        if retrieval_values:
            breakdown["retrieval_ms"] = {
                "min": min(retrieval_values),
                "max": max(retrieval_values),
                "avg": statistics.mean(retrieval_values),
                "p95": sorted(retrieval_values)[int(0.95 * (len(retrieval_values) - 1))] if len(retrieval_values) > 1 else retrieval_values[0],
            }

        generation_values = [l.generation_ms for l in self.latency_history if l.generation_ms is not None]
        if generation_values:
            breakdown["generation_ms"] = {
                "min": min(generation_values),
                "max": max(generation_values),
                "avg": statistics.mean(generation_values),
                "p95": sorted(generation_values)[int(0.95 * (len(generation_values) - 1))] if len(generation_values) > 1 else generation_values[0],
            }

        sql_values = [l.sql_ms for l in self.latency_history if l.sql_ms is not None]
        if sql_values:
            breakdown["sql_ms"] = {
                "min": min(sql_values),
                "max": max(sql_values),
                "avg": statistics.mean(sql_values),
                "p95": sorted(sql_values)[int(0.95 * (len(sql_values) - 1))] if len(sql_values) > 1 else sql_values[0],
            }

        if breakdown:
            summary["breakdown"] = breakdown

        return summary


def evaluate_latency(
    total_ms: float,
    retrieval_ms: Optional[float] = None,
    generation_ms: Optional[float] = None,
    sql_ms: Optional[float] = None,
    guardrails_ms: Optional[float] = None,
) -> LatencyBreakdown:
    """Create and validate a latency breakdown measurement.

    Args:
        total_ms: Total request time in milliseconds
        retrieval_ms: Vector search + retrieval time (optional)
        generation_ms: LLM generation time (optional)
        sql_ms: SQL execution time (optional)
        guardrails_ms: Guardrails validation time (optional)

    Returns:
        LatencyBreakdown with validated measurements
    """
    return LatencyBreakdown(
        total_ms=total_ms,
        retrieval_ms=retrieval_ms,
        generation_ms=generation_ms,
        sql_ms=sql_ms,
        guardrails_ms=guardrails_ms,
    )
