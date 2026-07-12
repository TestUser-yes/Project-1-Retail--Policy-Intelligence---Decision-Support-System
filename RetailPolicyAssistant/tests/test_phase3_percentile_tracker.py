"""Tests for Phase 3.1 percentile latency tracker."""

import pytest
from app.core.percentile_tracker import (
    LatencyPercentileTracker,
    get_latency_tracker,
    get_route_tracker,
    add_latency_sample,
    get_all_percentiles,
    reset_all_trackers,
)


class TestLatencyPercentileTracker:
    """Test latency percentile calculation."""

    def test_percentile_calculation_100_samples(self):
        """Test percentile calculation with 100 samples."""
        tracker = LatencyPercentileTracker()

        # Add 100 latency samples (0-99ms)
        for i in range(100):
            tracker.add_sample(float(i))

        percentiles = tracker.get_percentiles()

        assert percentiles["count"] == 100
        assert percentiles["p50"] == 50.0
        assert percentiles["p95"] >= 95.0
        assert percentiles["p99"] >= 99.0
        assert percentiles["min"] == 0.0
        assert percentiles["max"] == 99.0

    def test_percentile_calculation_1000_samples(self):
        """Test with 1000 samples for higher accuracy."""
        tracker = LatencyPercentileTracker()

        # Add 1000 latency samples
        for i in range(1000):
            tracker.add_sample(float(i % 500))  # Vary 0-499ms

        percentiles = tracker.get_percentiles()

        assert percentiles["count"] == 1000
        assert 200 <= percentiles["p50"] <= 300  # Rough estimate
        assert percentiles["p95"] >= percentiles["p50"]
        assert percentiles["p99"] >= percentiles["p95"]

    def test_empty_tracker(self):
        """Test empty tracker returns zeros."""
        tracker = LatencyPercentileTracker()
        percentiles = tracker.get_percentiles()

        assert percentiles["p50"] == 0
        assert percentiles["p95"] == 0
        assert percentiles["p99"] == 0
        assert percentiles["count"] == 0

    def test_summary_with_slo_target(self):
        """Test summary with SLO compliance."""
        tracker = LatencyPercentileTracker()

        # Add 100 samples: 80 within 2000ms, 20 above
        for i in range(80):
            tracker.add_sample(1000.0 + i * 10)  # 1000-1790ms (all < 2000ms)

        for i in range(20):
            tracker.add_sample(2500.0 + i * 100)  # 2500-4400ms (all > 2000ms)

        summary = tracker.get_summary(slo_target_ms=2000.0)

        assert summary["count"] == 100
        assert summary["compliance_pct"] == 80.0  # 80% within target
        assert summary["slo_target_ms"] == 2000.0

    def test_reset(self):
        """Test tracker reset."""
        tracker = LatencyPercentileTracker()

        tracker.add_sample(100.0)
        tracker.add_sample(200.0)
        assert tracker.get_percentiles()["count"] == 2

        tracker.reset()
        assert tracker.get_percentiles()["count"] == 0

    def test_window_cleanup(self):
        """Test that old samples are cleaned up."""
        import time
        from datetime import datetime, timedelta

        # Create tracker with very short window (100ms)
        tracker = LatencyPercentileTracker(window_size_ms=100)

        tracker.add_sample(10.0)
        assert len(tracker.latencies) == 1

        # Wait for window to expire
        time.sleep(0.15)  # 150ms

        # Add new sample (should trigger cleanup)
        tracker.add_sample(20.0)

        # Old sample should be cleaned up
        assert len(tracker.latencies) == 1


class TestGlobalTrackers:
    """Test global tracker instances."""

    def setup_method(self):
        """Reset trackers before each test."""
        reset_all_trackers()

    def test_global_tracker_singleton(self):
        """Test global tracker is singleton."""
        tracker1 = get_latency_tracker()
        tracker2 = get_latency_tracker()

        assert tracker1 is tracker2

    def test_route_tracker_creation(self):
        """Test route-specific trackers."""
        rag_tracker = get_route_tracker("rag")
        sql_tracker = get_route_tracker("sql")

        assert rag_tracker is not sql_tracker

    def test_add_latency_sample_global(self):
        """Test adding samples to global tracker."""
        add_latency_sample(100.0)
        add_latency_sample(200.0)
        add_latency_sample(150.0)

        percentiles = get_latency_tracker().get_percentiles()
        assert percentiles["count"] == 3

    def test_add_latency_sample_with_route(self):
        """Test adding samples to route-specific tracker."""
        add_latency_sample(100.0, route="rag")
        add_latency_sample(200.0, route="rag")
        add_latency_sample(150.0, route="sql")

        all_percentiles = get_all_percentiles()

        # Global should have 3 samples
        assert all_percentiles["global"]["count"] == 3

        # Route-specific
        assert all_percentiles["by_route"]["rag"]["count"] == 2
        assert all_percentiles["by_route"]["sql"]["count"] == 1

    def test_get_all_percentiles(self):
        """Test getting all percentiles."""
        # Add samples
        for i in range(50):
            add_latency_sample(float(i * 10), route="rag")

        for i in range(30):
            add_latency_sample(float(i * 15), route="sql")

        all_percentiles = get_all_percentiles(slo_target_ms=300.0)

        assert "global" in all_percentiles
        assert "by_route" in all_percentiles
        assert "rag" in all_percentiles["by_route"]
        assert "sql" in all_percentiles["by_route"]

        # Check compliance
        assert all_percentiles["global"]["compliance_pct"] > 0
        assert all_percentiles["by_route"]["rag"]["compliance_pct"] > 0


class TestLatencyMetrics:
    """Test latency metric calculations."""

    def setup_method(self):
        """Reset trackers before each test."""
        reset_all_trackers()

    def test_realistic_latency_distribution(self):
        """Test with realistic latency distribution."""
        # Simulate realistic query latencies
        latencies = [
            # Fast queries (< 1s)
            *[100 + i * 10 for i in range(60)],
            # Medium queries (1-3s)
            *[1000 + i * 50 for i in range(30)],
            # Slow queries (> 3s)
            *[3000 + i * 100 for i in range(10)],
        ]

        for lat in latencies:
            add_latency_sample(float(lat))

        tracker = get_latency_tracker()
        summary = tracker.get_summary(slo_target_ms=2000.0)

        # Verify statistics
        assert summary["count"] == len(latencies)
        assert summary["p50"] < 2000  # Median < 2s
        assert summary["p95"] >= summary["p50"]
        assert summary["p99"] >= summary["p95"]

        # Compliance should be high but not 100%
        compliance = summary["compliance_pct"]
        assert 70 <= compliance <= 100

    def test_multiple_route_tracking(self):
        """Test tracking multiple routes independently."""
        # RAG: fast (100-500ms)
        for i in range(50):
            add_latency_sample(100 + i * 8, route="rag")

        # SQL: slow (1000-3000ms)
        for i in range(30):
            add_latency_sample(1000 + i * 60, route="sql")

        # Hybrid: medium (500-1500ms)
        for i in range(20):
            add_latency_sample(500 + i * 50, route="hybrid")

        all_percentiles = get_all_percentiles(slo_target_ms=2000.0)

        rag_p95 = all_percentiles["by_route"]["rag"]["p95"]
        sql_p95 = all_percentiles["by_route"]["sql"]["p95"]
        hybrid_p95 = all_percentiles["by_route"]["hybrid"]["p95"]

        # Verify different latency profiles
        assert rag_p95 < hybrid_p95 < sql_p95
        assert rag_p95 < 500
        assert sql_p95 > 2000


class TestSLOCompliance:
    """Test SLO compliance calculations."""

    def setup_method(self):
        """Reset trackers before each test."""
        reset_all_trackers()

    def test_slo_compliance_calculation(self):
        """Test SLO compliance percentage."""
        slo_target = 2000.0

        # 75 samples within target
        for i in range(75):
            add_latency_sample(1000.0 + i * 5)

        # 25 samples above target
        for i in range(25):
            add_latency_sample(2500.0 + i * 10)

        summary = get_latency_tracker().get_summary(slo_target_ms=slo_target)

        assert summary["compliance_pct"] == 75.0

    def test_slo_breach_detection(self):
        """Test detecting SLO breaches."""
        # All samples above target
        for i in range(30):
            add_latency_sample(5000.0 + i * 100)

        summary = get_latency_tracker().get_summary(slo_target_ms=2000.0)

        assert summary["compliance_pct"] == 0.0

    def test_perfect_slo_compliance(self):
        """Test perfect SLO compliance."""
        slo_target = 3000.0

        # All samples below target
        for i in range(100):
            add_latency_sample(500.0 + i * 20)

        summary = get_latency_tracker().get_summary(slo_target_ms=slo_target)

        assert summary["compliance_pct"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
