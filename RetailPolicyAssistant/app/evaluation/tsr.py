"""Task Success Rate (TSR) evaluation - tracks successful vs failed queries."""

from dataclasses import dataclass
from typing import Optional
from collections import deque


@dataclass
class TSRMetrics:
    """Task Success Rate metrics."""

    successful_queries: int = 0
    total_queries: int = 0
    tsr: float = 0.0  # Successful / Total (0.0-1.0)
    last_updated: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "successful_queries": self.successful_queries,
            "total_queries": self.total_queries,
            "tsr": round(self.tsr, 4),
            "tsr_percent": round(self.tsr * 100, 2),
            "last_updated": self.last_updated,
        }


class TSRCalculator:
    """Calculate Task Success Rate over a rolling window."""

    def __init__(self, window_size: int = 1000):
        """Initialize TSR calculator.

        Args:
            window_size: Number of recent queries to track for rolling TSR
        """
        self.window_size = window_size
        self.query_results = deque(maxlen=window_size)  # True = success, False = failure

        # Global counters (not rolling)
        self.total_success = 0
        self.total_count = 0

    def record_query(self, success: bool) -> None:
        """Record the result of a query.

        Args:
            success: True if query succeeded, False otherwise
        """
        self.query_results.append(success)
        self.total_count += 1
        if success:
            self.total_success += 1

    def get_rolling_tsr(self) -> float:
        """Get TSR for the rolling window of recent queries.

        Returns:
            TSR value (0.0-1.0)
        """
        if not self.query_results:
            return 0.0

        successful = sum(1 for result in self.query_results if result)
        return successful / len(self.query_results)

    def get_global_tsr(self) -> float:
        """Get overall TSR across all queries.

        Returns:
            TSR value (0.0-1.0)
        """
        if self.total_count == 0:
            return 0.0
        return self.total_success / self.total_count

    def get_metrics(self) -> TSRMetrics:
        """Get current TSR metrics.

        Returns:
            TSRMetrics with rolling window values
        """
        if not self.query_results:
            return TSRMetrics()

        successful = sum(1 for result in self.query_results if result)
        total = len(self.query_results)
        tsr = successful / total if total > 0 else 0.0

        return TSRMetrics(
            successful_queries=successful,
            total_queries=total,
            tsr=tsr,
        )

    def get_summary(self) -> dict:
        """Get comprehensive TSR summary.

        Returns:
            {
                "rolling_window": {
                    "successful": int,
                    "total": int,
                    "tsr": float,
                    "tsr_percent": float,
                },
                "global": {
                    "successful": int,
                    "total": int,
                    "tsr": float,
                    "tsr_percent": float,
                },
                "status": "good" | "warning" | "critical"
            }
        """
        rolling_tsr = self.get_rolling_tsr()
        global_tsr = self.get_global_tsr()

        rolling_successful = sum(1 for result in self.query_results if result)
        rolling_total = len(self.query_results)

        # Determine status
        if rolling_tsr >= 0.95:
            status = "good"
        elif rolling_tsr >= 0.90:
            status = "warning"
        else:
            status = "critical"

        return {
            "rolling_window": {
                "successful": rolling_successful,
                "total": rolling_total,
                "tsr": round(rolling_tsr, 4),
                "tsr_percent": round(rolling_tsr * 100, 2),
            },
            "global": {
                "successful": self.total_success,
                "total": self.total_count,
                "tsr": round(global_tsr, 4),
                "tsr_percent": round(global_tsr * 100, 2),
            },
            "status": status,
        }

    def reset(self) -> None:
        """Reset all counters (for testing)."""
        self.query_results.clear()
        self.total_success = 0
        self.total_count = 0


# Global singleton instance
_tsr_calculator: Optional[TSRCalculator] = None


def get_tsr_calculator() -> TSRCalculator:
    """Get the global TSR calculator instance."""
    global _tsr_calculator
    if _tsr_calculator is None:
        _tsr_calculator = TSRCalculator()
    return _tsr_calculator


def record_query_success(success: bool) -> None:
    """Record a query result in the global TSR tracker.

    Args:
        success: True if query succeeded, False if it failed
    """
    calculator = get_tsr_calculator()
    calculator.record_query(success)


def get_current_tsr() -> float:
    """Get current rolling window TSR.

    Returns:
        TSR value (0.0-1.0)
    """
    calculator = get_tsr_calculator()
    return calculator.get_rolling_tsr()


def evaluate_query_success(
    response: dict,
    escalated: bool = False,
    error_occurred: bool = False,
) -> bool:
    """Determine if a query was successful based on response details.

    Args:
        response: Orchestrator response dict
        escalated: Whether query was escalated
        error_occurred: Whether an error occurred

    Returns:
        True if successful, False otherwise
    """
    # Query is successful if:
    # 1. No error occurred
    # 2. Not escalated due to security or system issues
    # 3. Response contains valid result

    if error_occurred:
        return False

    if escalated:
        # Check escalation reason to determine if it's a system failure or policy escalation
        escalation_reason = response.get("escalation_reason", "").lower()
        # Escalate due to high-risk content is still "successful" (system worked)
        # But escalate due to guardrails violation or system error is not
        if any(keyword in escalation_reason for keyword in ["security", "guardrail", "rbac", "error", "system"]):
            return False

    # Check if result is present
    result = response.get("result", {})
    if isinstance(result, dict):
        result_text = result.get("result", "")
    else:
        result_text = str(result)

    # Empty result = not successful
    if not result_text or "error" in result_text.lower():
        return False

    return True
