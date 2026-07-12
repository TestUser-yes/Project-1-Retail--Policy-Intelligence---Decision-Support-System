"""Tests for Phase 3.2 error budget and user SLO profiles."""

import pytest
from datetime import datetime, timedelta
from app.core.error_budget import (
    ErrorBudgetCalculator,
    BudgetConfig,
    ErrorEvent,
    get_error_budget_calculator,
    record_slo_error,
)
from app.core.user_slo_profiles import (
    UserSLOProfileManager,
    UserTier,
    get_user_slo_profile_manager,
    get_user_profile,
    check_user_limits,
)


class TestErrorBudget:
    """Test error budget calculation."""

    def test_budget_creation(self):
        """Test budget window creation."""
        budget = ErrorBudgetCalculator()
        window = budget.get_current_window()

        assert window is not None
        assert window.total_budget_percent > 0  # SLO 99.5% = 0.5% budget
        assert window.consumed_percent == 0
        assert window.remaining_percent() > 0

    def test_add_single_error(self):
        """Test adding a single error."""
        budget = ErrorBudgetCalculator()
        budget.add_error("latency", "normal", "Query exceeded target")

        window = budget.get_current_window()
        assert len(window.errors) == 1
        assert window.consumed_percent > 0

    def test_error_severity_weighting(self):
        """Test that severity affects budget consumption."""
        budget = ErrorBudgetCalculator()

        # Add normal error (weight 1.0)
        budget.add_error("latency", "normal")
        normal_consumed = budget.get_current_window().consumed_percent

        # Reset
        budget = ErrorBudgetCalculator()

        # Add critical error (weight 2.0)
        budget.add_error("latency", "critical")
        critical_consumed = budget.get_current_window().consumed_percent

        # Critical should consume twice as much
        assert critical_consumed > normal_consumed

    def test_budget_status(self):
        """Test budget status report."""
        budget = ErrorBudgetCalculator()
        budget.add_error("latency", "normal")
        budget.add_error("latency", "high")

        status = budget.get_budget_status()

        assert "month" in status
        assert "consumed_percent" in status
        assert "remaining_percent" in status
        assert "burn_rate_multiplier" in status
        assert "status" in status  # ok, warning, critical, exhausted
        assert status["status"] in ["ok", "warning", "critical", "exhausted"]

    def test_budget_exhaustion_detection(self):
        """Test detection of exhausted budget."""
        budget = ErrorBudgetCalculator()
        window = budget.get_current_window()

        # Add enough errors to exceed budget
        for _ in range(int(window.total_budget_percent * 150)):  # 150% of budget
            budget.add_error("latency", "normal")

        assert window.is_exhausted()

        status = budget.get_budget_status()
        assert status["status"] == "exhausted"

    def test_burn_rate_calculation(self):
        """Test burn rate multiplier calculation."""
        budget = ErrorBudgetCalculator()

        # Add errors over time
        for _ in range(10):
            budget.add_error("latency", "normal")

        status = budget.get_budget_status()

        # Burn rate should be calculable
        assert status["burn_rate_multiplier"] >= 0
        assert "expected_daily_burn" in status
        assert "actual_daily_burn" in status

    def test_recovery_plan(self):
        """Test recovery plan generation."""
        budget = ErrorBudgetCalculator()

        # Add moderate errors
        for _ in range(5):
            budget.add_error("latency", "normal")

        plan = budget.get_recovery_plan()

        assert "status" in plan
        assert "actions" in plan
        assert "recommendation" in plan

    def test_burn_rate_analysis(self):
        """Test burn rate analysis by period."""
        budget = ErrorBudgetCalculator()

        # Add recent errors
        for _ in range(5):
            budget.add_error("latency", "normal")

        analysis = budget.get_burn_rate_analysis()

        assert "period_analysis" in analysis
        assert "error_types" in analysis
        assert "severity_distribution" in analysis

    def test_error_type_analysis(self):
        """Test analysis of errors by type."""
        budget = ErrorBudgetCalculator()

        # Add various error types
        budget.add_error("latency", "normal")
        budget.add_error("latency", "normal")
        budget.add_error("error", "high")
        budget.add_error("availability", "critical")

        analysis = budget.get_burn_rate_analysis()
        error_types = analysis["error_types"]

        assert error_types["latency"] == 2
        assert error_types["error"] == 1
        assert error_types["availability"] == 1


class TestUserSLOProfiles:
    """Test user SLO profiles."""

    def test_tier_profiles_exist(self):
        """Test that all tier profiles are defined."""
        manager = UserSLOProfileManager()

        for tier in UserTier:
            profile = manager.get_profile(f"user_tier_{tier.value}")
            assert profile is not None
            assert profile.latency_target_ms > 0
            assert profile.confidence_min > 0

    def test_tier_hierarchy(self):
        """Test that tier thresholds are properly ordered."""
        manager = UserSLOProfileManager()

        # Latency should be: Trial (relaxed) > Standard > Premium > Enterprise (strict)
        trial = manager.get_profile("user_tier_trial")
        standard = manager.get_profile("user_tier_standard")
        premium = manager.get_profile("user_tier_premium")
        enterprise = manager.get_profile("user_tier_enterprise")

        # Trial should have most relaxed latency target
        assert trial.latency_target_ms > standard.latency_target_ms
        assert standard.latency_target_ms > premium.latency_target_ms
        assert premium.latency_target_ms > enterprise.latency_target_ms

    def test_custom_profile(self):
        """Test setting custom profile for user."""
        manager = UserSLOProfileManager()

        from app.core.user_slo_profiles import SLOThresholds

        custom = SLOThresholds(
            latency_target_ms=1000.0,
            latency_hard_limit_ms=2000.0,
            latency_soft_warning_ms=1500.0,
            confidence_min=0.80,
            confidence_escalate_threshold=0.60,
            error_rate_max_percent=0.1,
            availability_slo_percent=99.9,
        )

        manager.set_custom_profile("custom_user", custom)
        profile = manager.get_profile("custom_user")

        assert profile.latency_target_ms == 1000.0
        assert profile.confidence_min == 0.80

    def test_latency_threshold_retrieval(self):
        """Test getting latency thresholds."""
        manager = UserSLOProfileManager()
        thresholds = manager.get_latency_threshold("any_user")

        assert "target_ms" in thresholds
        assert "soft_warning_ms" in thresholds
        assert "hard_limit_ms" in thresholds

    def test_rate_limits_retrieval(self):
        """Test getting rate limits."""
        manager = UserSLOProfileManager()
        limits = manager.get_rate_limits("any_user")

        assert "queries_per_hour" in limits
        assert "queries_per_day" in limits
        assert "concurrent_queries" in limits

    def test_limit_check_within_bounds(self):
        """Test checking if query is within limits."""
        manager = UserSLOProfileManager()

        # Query within limits
        result = manager.is_within_limits(
            "any_user",
            latency_ms=1500.0,  # Within standard target of 2500ms
            confidence=0.75,  # Above standard minimum of 0.50
        )

        assert result["within_limits"] is True
        assert result["latency_ok"] is True
        assert result["confidence_ok"] is True
        assert len(result["actions"]) == 0

    def test_limit_check_exceeds_target(self):
        """Test checking when latency exceeds target."""
        manager = UserSLOProfileManager()

        # Latency exceeds target but not hard limit
        result = manager.is_within_limits(
            "any_user",
            latency_ms=3500.0,  # Between target (2500) and warning (3500)
            confidence=0.75,
        )

        assert result["latency_ok"] is False
        assert "warn" in result["actions"]

    def test_limit_check_exceeds_hard_limit(self):
        """Test checking when latency exceeds hard limit."""
        manager = UserSLOProfileManager()

        # Latency exceeds hard limit
        result = manager.is_within_limits(
            "any_user",
            latency_ms=6000.0,  # Above hard limit of 5000
            confidence=0.75,
        )

        assert result["latency_ok"] is False
        assert "reject" in result["actions"]

    def test_limit_check_low_confidence(self):
        """Test checking with low confidence."""
        manager = UserSLOProfileManager()

        # Low confidence, escalate
        result = manager.is_within_limits(
            "any_user",
            latency_ms=1500.0,
            confidence=0.25,  # Below escalate threshold of 0.30
        )

        assert result["confidence_ok"] is False
        assert "escalate" in result["actions"]

    def test_profile_summary(self):
        """Test profile summary generation."""
        manager = UserSLOProfileManager()
        summary = manager.get_profile_summary("any_user")

        assert "user_id" in summary
        assert "tier" in summary
        assert "latency_targets" in summary
        assert "confidence_thresholds" in summary
        assert "rate_limits" in summary
        assert "features" in summary

    def test_global_profile_manager(self):
        """Test global profile manager singleton."""
        manager1 = get_user_slo_profile_manager()
        manager2 = get_user_slo_profile_manager()

        assert manager1 is manager2


class TestBudgetIntegration:
    """Test integration between budget and profiles."""

    def test_budget_status_with_profile(self):
        """Test that budget respects user profiles."""
        budget = ErrorBudgetCalculator()
        manager = UserSLOProfileManager()

        # Add errors
        budget.add_error("latency", "normal")
        budget.add_error("latency", "high")

        status = budget.get_budget_status()
        profile = manager.get_profile("any_user")

        # Status should reference SLO
        assert status["total_budget_percent"] > 0
        assert profile.availability_slo_percent > 0

    def test_error_recording(self):
        """Test global error recording."""
        from app.core.error_budget import record_slo_error

        record_slo_error("latency", "normal", "Test error")

        calculator = get_error_budget_calculator()
        status = calculator.get_budget_status()

        assert status["consumed_percent"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
