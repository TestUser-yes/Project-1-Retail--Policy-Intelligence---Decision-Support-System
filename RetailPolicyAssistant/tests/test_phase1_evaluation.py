"""Unit tests for Phase 1 evaluation metrics."""

import pytest
import asyncio
from app.evaluation.config import (
    get_evaluation_config, load_evaluation_config, get_metric_status,
    is_metric_enabled, reset_evaluation_config
)
from app.evaluation.latency_breakdown import (
    LatencyBreakdown, LatencyMetricCalculator, evaluate_latency
)
from app.evaluation.tsr import (
    TSRCalculator, evaluate_query_success, get_tsr_calculator
)
from app.evaluation.sql_correctness import (
    SQLValidator, validate_sql, SQLCorrectnessTracker
)
from app.evaluation.phase1_orchestrator import (
    Phase1Evaluator, evaluate_phase1
)


class TestEvaluationConfig:
    """Test evaluation configuration system."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        reset_evaluation_config()
        config = load_evaluation_config()

        # Phase 1 should be enabled by default
        assert config.enable_latency is True
        assert config.enable_tsr is True
        assert config.enable_sql_correctness is True

        # Phase 4 should be disabled by default
        assert config.enable_accuracy is False

    def test_metric_status_latency(self):
        """Test metric status determination for latency."""
        assert get_metric_status("latency_ms", 1500) == "good"
        assert get_metric_status("latency_ms", 2500) == "warning"
        assert get_metric_status("latency_ms", 6000) == "critical"

    def test_metric_status_tsr(self):
        """Test metric status determination for TSR."""
        assert get_metric_status("tsr", 0.95) == "good"
        assert get_metric_status("tsr", 0.92) == "warning"
        assert get_metric_status("tsr", 0.88) == "critical"

    def test_is_metric_enabled(self):
        """Test metric enabled check."""
        reset_evaluation_config()
        assert is_metric_enabled("latency") is True
        assert is_metric_enabled("tsr") is True
        assert is_metric_enabled("sql_correctness") is True
        assert is_metric_enabled("accuracy") is False


class TestLatencyBreakdown:
    """Test latency breakdown metric."""

    def test_latency_breakdown_creation(self):
        """Test creating a latency breakdown."""
        latency = LatencyBreakdown(
            total_ms=1500,
            retrieval_ms=200,
            generation_ms=1000,
            sql_ms=50
        )
        assert latency.total_ms == 1500
        assert latency.retrieval_ms == 200

    def test_latency_breakdown_validation(self):
        """Test latency validation."""
        with pytest.raises(ValueError):
            LatencyBreakdown(total_ms=-100)

    def test_latency_calculator_percentile(self):
        """Test latency percentile calculation."""
        calc = LatencyMetricCalculator()

        # Add some latencies
        for ms in [100, 200, 300, 400, 500]:
            calc.record_latency(LatencyBreakdown(total_ms=ms))

        p50 = calc.get_percentile(0.50)
        p95 = calc.get_percentile(0.95)

        assert p50 == 300  # Median
        assert p95 >= 400

    def test_latency_calculator_average_breakdown(self):
        """Test average latency breakdown calculation."""
        calc = LatencyMetricCalculator()

        for i in range(3):
            calc.record_latency(LatencyBreakdown(
                total_ms=1000 + i * 100,
                retrieval_ms=200 + i * 10,
                generation_ms=700 + i * 50
            ))

        avg = calc.get_average_breakdown()
        assert avg is not None
        assert 1000 <= avg.total_ms <= 1200
        assert avg.retrieval_ms is not None

    def test_latency_calculator_summary(self):
        """Test latency summary generation."""
        calc = LatencyMetricCalculator()

        for ms in [1000, 1500, 2000, 2500]:
            calc.record_latency(LatencyBreakdown(total_ms=ms))

        summary = calc.get_summary()
        assert summary["count"] == 4
        assert "total_ms" in summary
        assert summary["total_ms"]["avg"] == 1750.0


class TestTSR:
    """Test Task Success Rate metric."""

    def test_tsr_calculator_basic(self):
        """Test basic TSR calculation."""
        calc = TSRCalculator()

        calc.record_query(True)
        calc.record_query(True)
        calc.record_query(False)

        tsr = calc.get_rolling_tsr()
        assert tsr == pytest.approx(2/3, rel=0.01)

    def test_tsr_calculator_window(self):
        """Test TSR rolling window."""
        calc = TSRCalculator(window_size=5)

        # Fill window
        for _ in range(5):
            calc.record_query(True)
        assert calc.get_rolling_tsr() == 1.0

        # Add failing query (should drop oldest true from window)
        calc.record_query(False)
        assert calc.get_rolling_tsr() == 0.8

    def test_tsr_evaluate_query_success(self):
        """Test query success evaluation."""
        response_success = {
            "result": {"result": "This is a valid answer"},
            "escalate": False
        }
        assert evaluate_query_success(response_success) is True

        response_error = {
            "result": {"result": "Error: something failed"},
            "escalate": False
        }
        assert evaluate_query_success(response_error) is False

        response_empty = {
            "result": {"result": ""},
            "escalate": False
        }
        assert evaluate_query_success(response_empty) is False

    def test_tsr_global_counter(self):
        """Test TSR global counter."""
        calc = TSRCalculator(window_size=10)

        # Add queries beyond window size
        for i in range(20):
            calc.record_query(i % 2 == 0)  # Alternate success/fail

        # Global should count all 20
        assert calc.total_count == 20

        # Rolling window should only have 10
        assert len(calc.query_results) == 10


class TestSQLCorrectness:
    """Test SQL correctness evaluation."""

    def test_sql_validator_valid_query(self):
        """Test validation of valid SQL query."""
        validator = SQLValidator()

        result = validator.evaluate_query(
            query="SELECT * FROM users WHERE id = 1",
            execution_succeeded=True,
            row_count=1
        )

        assert result.syntax_valid is True
        assert result.injection_safe is True
        assert result.is_correct is True

    def test_sql_validator_injection_detection(self):
        """Test SQL injection detection."""
        validator = SQLValidator()

        result = validator.evaluate_query(
            query="SELECT * FROM users WHERE id = 1 OR 1=1",
            execution_succeeded=True
        )

        assert result.injection_safe is False
        assert result.is_correct is False

    def test_sql_validator_syntax_error(self):
        """Test syntax error detection."""
        validator = SQLValidator()

        result = validator.evaluate_query(
            query="SELECT * FROM ((users",
            execution_succeeded=True
        )

        assert result.syntax_valid is False

    def test_sql_validator_execution_error(self):
        """Test execution error detection."""
        validator = SQLValidator()

        result = validator.evaluate_query(
            query="SELECT * FROM nonexistent_table",
            execution_succeeded=False,
            execution_error="Table not found"
        )

        assert result.execution_successful is False
        assert result.is_correct is False

    def test_sql_correctness_tracker_summary(self):
        """Test SQL correctness tracking summary."""
        tracker = SQLCorrectnessTracker()

        # Add some results
        result1 = validate_sql("SELECT * FROM users WHERE id = 1", True)
        result2 = validate_sql("SELECT * FROM users WHERE id = 1 OR 1=1", True)

        tracker.record_evaluation(result1)
        tracker.record_evaluation(result2)

        summary = tracker.get_summary()
        assert summary["total_queries"] == 2
        assert summary["correct_queries"] == 1


class TestPhase1Evaluator:
    """Test Phase 1 orchestrator."""

    def test_phase1_evaluation_basic(self):
        """Test basic Phase 1 evaluation."""
        response = {
            "result": {"result": "Test answer"},
            "route": "rag",
            "escalate": False
        }

        # Run async function in event loop
        result = asyncio.run(evaluate_phase1(
            response=response,
            query="Test query",
            route="rag",
            retrieval_ms=150,
            generation_ms=800,
            total_latency_ms=1200
        ))

        assert result.latency is not None
        assert result.latency.total_ms == 1200
        assert result.success is True

    def test_phase1_evaluation_with_sql(self):
        """Test Phase 1 evaluation with SQL."""
        response = {
            "result": {"result": "5 results"},
            "route": "sql",
            "escalate": False
        }

        result = asyncio.run(evaluate_phase1(
            response=response,
            query="How many users?",
            route="sql",
            sql_query="SELECT COUNT(*) FROM users",
            sql_execution_succeeded=True,
            total_latency_ms=500
        ))

        assert result.sql_correctness is not None
        assert result.sql_correctness.execution_successful is True


class TestPhase1Integration:
    """Integration tests for Phase 1 metrics."""

    def test_phase1_full_workflow(self):
        """Test full Phase 1 workflow."""
        # Create calculator instances
        latency_calc = LatencyMetricCalculator()
        tsr_calc = TSRCalculator()
        sql_tracker = SQLCorrectnessTracker()

        # Simulate 10 queries
        for i in range(10):
            # Record latency
            latency = LatencyBreakdown(
                total_ms=1000 + i * 100,
                retrieval_ms=200 + i * 10,
                generation_ms=700 + i * 80
            )
            latency_calc.record_latency(latency)

            # Record TSR
            success = i % 3 != 0  # 2/3 success rate
            tsr_calc.record_query(success)

            # Record SQL (if applicable)
            if i % 2 == 0:
                sql_result = validate_sql(
                    "SELECT * FROM users LIMIT 10",
                    execution_succeeded=True,
                    row_count=10
                )
                sql_tracker.record_evaluation(sql_result)

        # Verify aggregation
        latency_summary = latency_calc.get_summary()
        tsr_summary = tsr_calc.get_summary()
        sql_summary = sql_tracker.get_summary()

        assert latency_summary["count"] == 10
        assert tsr_summary["rolling_window"]["total"] == 10
        assert sql_summary["total_queries"] == 5

        # Verify TSR is approximately 2/3
        tsr = tsr_summary["rolling_window"]["tsr"]
        assert 0.55 <= tsr <= 0.75  # Approximately 2/3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
