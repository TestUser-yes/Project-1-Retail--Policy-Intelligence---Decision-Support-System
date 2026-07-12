"""Percentile latency tracking for SLO compliance.

Tracks p50, p95, p99 latency percentiles over rolling time windows.
Used by Phase 3.1 for SLO metrics collection.
"""

from typing import List, Dict, Optional
from collections import deque
from datetime import datetime, timedelta


class LatencyPercentileTracker:
    """Tracks latency percentiles (p50, p95, p99) over time windows."""

    def __init__(self, window_size_ms: int = 3600000):
        """Initialize tracker with time window.

        Args:
            window_size_ms: Time window in milliseconds (default 1 hour = 3600000ms)
        """
        self.window_size_ms = window_size_ms
        self.latencies: deque = deque()  # [(timestamp, latency_ms), ...]

    def add_sample(self, latency_ms: float):
        """Add a latency sample.

        Args:
            latency_ms: Latency in milliseconds
        """
        self.latencies.append((datetime.utcnow(), latency_ms))
        self._cleanup_old_samples()

    def _cleanup_old_samples(self):
        """Remove samples older than the configured window."""
        cutoff = datetime.utcnow() - timedelta(milliseconds=self.window_size_ms)
        while self.latencies and self.latencies[0][0] < cutoff:
            self.latencies.popleft()

    def get_percentiles(self) -> Dict[str, float]:
        """Calculate p50, p95, p99 percentiles.

        Returns:
            {
                "p50": float,      # Median latency
                "p95": float,      # 95th percentile
                "p99": float,      # 99th percentile
                "min": float,      # Minimum latency
                "max": float,      # Maximum latency
                "mean": float,     # Mean latency
                "count": int,      # Number of samples
            }
        """
        if not self.latencies:
            return {
                "p50": 0,
                "p95": 0,
                "p99": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
                "count": 0,
            }

        # Extract latencies and sort
        sorted_latencies = sorted([lat for _, lat in self.latencies])
        n = len(sorted_latencies)

        def percentile(p):
            """Calculate percentile value."""
            idx = int((p / 100.0) * (n - 1))
            idx = max(0, min(idx, n - 1))
            return sorted_latencies[idx]

        total = sum(sorted_latencies)
        mean = total / n if n > 0 else 0

        return {
            "p50": round(percentile(50), 2),
            "p95": round(percentile(95), 2),
            "p99": round(percentile(99), 2),
            "min": round(min(sorted_latencies), 2),
            "max": round(max(sorted_latencies), 2),
            "mean": round(mean, 2),
            "count": n,
        }

    def get_summary(self, slo_target_ms: float = 2000.0) -> Dict:
        """Get percentile summary with SLO compliance.

        Args:
            slo_target_ms: SLO target latency in milliseconds (default 2000ms)

        Returns:
            Percentiles dict plus compliance percentage
        """
        percentiles = self.get_percentiles()

        # Count how many are within target
        if self.latencies:
            compliant = sum(1 for _, lat in self.latencies if lat <= slo_target_ms)
            compliance_pct = (compliant / len(self.latencies)) * 100
        else:
            compliance_pct = 0

        return {
            **percentiles,
            "slo_target_ms": slo_target_ms,
            "compliance_pct": round(compliance_pct, 2),
        }

    def reset(self):
        """Clear all samples."""
        self.latencies.clear()

    def get_stats_by_route(self) -> Dict[str, Dict]:
        """Get latency stats (for future use with per-route tracking).

        Returns:
            Dictionary with overall stats
        """
        percentiles = self.get_percentiles()
        return {
            "overall": percentiles,
            "window_ms": self.window_size_ms,
        }


# Global tracker instances
_latency_tracker: Optional[LatencyPercentileTracker] = None
_route_trackers: Dict[str, LatencyPercentileTracker] = {}


def get_latency_tracker() -> LatencyPercentileTracker:
    """Get or create global latency tracker instance."""
    global _latency_tracker
    if _latency_tracker is None:
        _latency_tracker = LatencyPercentileTracker(window_size_ms=3600000)
    return _latency_tracker


def get_route_tracker(route: str) -> LatencyPercentileTracker:
    """Get or create route-specific latency tracker.

    Args:
        route: Route identifier (e.g., 'rag', 'sql', 'hybrid')

    Returns:
        LatencyPercentileTracker for this route
    """
    if route not in _route_trackers:
        _route_trackers[route] = LatencyPercentileTracker(window_size_ms=3600000)
    return _route_trackers[route]


def add_latency_sample(latency_ms: float, route: Optional[str] = None):
    """Add a latency sample to global and optionally route-specific trackers.

    Args:
        latency_ms: Latency in milliseconds
        route: Optional route identifier for per-route tracking
    """
    tracker = get_latency_tracker()
    tracker.add_sample(latency_ms)

    if route:
        route_tracker = get_route_tracker(route)
        route_tracker.add_sample(latency_ms)


def get_all_percentiles(slo_target_ms: float = 2000.0) -> Dict:
    """Get percentiles for all routes.

    Args:
        slo_target_ms: SLO target latency in milliseconds

    Returns:
        Dictionary with global and per-route percentiles
    """
    global_tracker = get_latency_tracker()

    result = {
        "global": global_tracker.get_summary(slo_target_ms),
        "by_route": {},
    }

    for route, tracker in _route_trackers.items():
        result["by_route"][route] = tracker.get_summary(slo_target_ms)

    return result


def reset_all_trackers():
    """Reset all trackers (for testing)."""
    global _latency_tracker, _route_trackers
    if _latency_tracker:
        _latency_tracker.reset()
    for tracker in _route_trackers.values():
        tracker.reset()
    _route_trackers.clear()
