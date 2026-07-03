"""SLO (Service Level Objective) tracking and compliance monitoring."""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SLOMetrics:
    """Tracks actual performance against SLO targets."""
    latency_ms: float
    target_latency_ms: float = 2000.0  # 2 seconds default
    slo_status: str = "pass"  # pass, warning, fail
    accuracy_score: Optional[float] = None
    route_accuracy: Optional[float] = None
    escalation_rate: Optional[float] = None


class SLOTracker:
    """Tracks and validates SLO compliance for queries."""

    # SLO targets from app/evaluation/slos.py
    TARGETS = {
        "latency_seconds": 2.0,
        "p95_latency_seconds": 3.0,
        "route_accuracy": 0.95,
        "answer_accuracy": 0.90,
        "risk_accuracy": 0.95,
        "escalation_accuracy": 1.00,
    }

    # Warning thresholds (80% of target)
    WARNING_THRESHOLDS = {
        "latency_seconds": 1.6,  # 80% of 2.0
        "p95_latency_seconds": 2.4,  # 80% of 3.0
    }

    def __init__(self):
        self.metrics_history: list[SLOMetrics] = []
        self.query_count = 0
        self.escalation_count = 0

    def record_latency(self, latency_seconds: float) -> SLOMetrics:
        """Record query latency and check SLO compliance.

        Args:
            latency_seconds: Query execution time in seconds

        Returns:
            SLOMetrics with compliance status
        """
        latency_ms = latency_seconds * 1000
        target_latency_ms = self.TARGETS["latency_seconds"] * 1000

        # Determine SLO status
        if latency_ms <= target_latency_ms:
            slo_status = "pass"
        elif latency_ms <= self.WARNING_THRESHOLDS["latency_seconds"] * 1000:
            slo_status = "warning"
        else:
            slo_status = "fail"

        metrics = SLOMetrics(
            latency_ms=round(latency_ms, 2),
            target_latency_ms=target_latency_ms,
            slo_status=slo_status,
        )

        self.metrics_history.append(metrics)
        return metrics

    def record_query_outcome(self, success: bool) -> None:
        """Record whether query was processed successfully."""
        self.query_count += 1

    def record_escalation(self) -> None:
        """Record an escalation event."""
        self.escalation_count += 1

    def get_escalation_rate(self) -> float:
        """Get percentage of queries escalated."""
        if self.query_count == 0:
            return 0.0
        return round((self.escalation_count / self.query_count) * 100, 2)

    def get_average_latency(self) -> float:
        """Get average latency across all recorded queries."""
        if not self.metrics_history:
            return 0.0
        total = sum(m.latency_ms for m in self.metrics_history)
        return round(total / len(self.metrics_history), 2)

    def get_slo_compliance_rate(self) -> float:
        """Get percentage of queries meeting SLO targets."""
        if not self.metrics_history:
            return 100.0
        passed = sum(1 for m in self.metrics_history if m.slo_status == "pass")
        return round((passed / len(self.metrics_history)) * 100, 2)

    def get_summary(self) -> Dict:
        """Get SLO compliance summary."""
        return {
            "total_queries": self.query_count,
            "total_escalations": self.escalation_count,
            "escalation_rate_percent": self.get_escalation_rate(),
            "average_latency_ms": self.get_average_latency(),
            "slo_compliance_rate_percent": self.get_slo_compliance_rate(),
            "target_latency_ms": self.TARGETS["latency_seconds"] * 1000,
        }


# Global SLO tracker instance
_slo_tracker: Optional[SLOTracker] = None


def get_slo_tracker() -> SLOTracker:
    """Get or create global SLO tracker instance."""
    global _slo_tracker
    if _slo_tracker is None:
        _slo_tracker = SLOTracker()
    return _slo_tracker
