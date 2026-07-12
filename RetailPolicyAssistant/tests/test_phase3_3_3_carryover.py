"""Tests for Phase 3.3.3 budget carryover logic."""

import pytest
from datetime import datetime
from uuid import uuid4
from app.core.budget_carryover import (
    BudgetCarryoverManager,
    get_carryover_manager,
)


class TestCarryoverCalculation:
    """Test carryover amount calculations."""

    def test_high_efficiency_carryover(self):
        """Test carryover for high efficiency (< 50% consumption)."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.2% (40% used) → carry 100% of 0.3%
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.2,
        )

        assert carryover == 0.3
        assert carryover <= 0.5 * manager.MAX_CARRYOVER_MULTIPLIER

    def test_medium_efficiency_carryover(self):
        """Test carryover for medium efficiency (50-80% consumption)."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.3% (60% used) → carry 50% of 0.2%
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.3,
        )

        assert carryover == 0.1
        assert 0.0 < carryover < 0.2

    def test_low_efficiency_carryover(self):
        """Test carryover for low efficiency (> 80% consumption)."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.45% (90% used) → carry 0%
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.45,
        )

        assert carryover == 0.0

    def test_carryover_max_cap(self):
        """Test carryover is capped at 1x monthly budget."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.0% → should carry 0.5% max (not unlimited)
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.0,
        )

        assert carryover == 0.5
        assert carryover <= 0.5 * manager.MAX_CARRYOVER_MULTIPLIER

    def test_budget_exhausted_no_carryover(self):
        """Test no carryover when budget exhausted."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.5% → carry 0%
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.5,
        )

        assert carryover == 0.0

    def test_budget_exceeded_no_carryover(self):
        """Test no carryover when budget exceeded."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.7% (over budget) → carry 0%
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.7,
        )

        assert carryover == 0.0

    def test_edge_case_zero_consumption(self):
        """Test carryover with zero consumption."""
        manager = BudgetCarryoverManager()

        # Budget 0.5%, consumed 0.0% → carry full budget (high efficiency)
        carryover = manager.calculate_carryover(
            monthly_budget=0.5,
            consumed_percent=0.0,
        )

        assert carryover == 0.5  # Full budget carried

    def test_edge_case_threshold_boundary(self):
        """Test carryover at efficiency threshold boundary."""
        manager = BudgetCarryoverManager()

        # Budget 1.0%, consumed exactly 50% (0.5%)
        carryover = manager.calculate_carryover(
            monthly_budget=1.0,
            consumed_percent=0.5,
        )

        # At 50% boundary → should use medium rate (50%)
        assert carryover == 0.25  # 50% of 0.5% unused


class TestRecoveryCredits:
    """Test recovery credit calculations."""

    def test_no_efficient_months(self):
        """Test recovery credits with no efficient months."""
        manager = BudgetCarryoverManager()

        # No efficient months (all consumed > 25% of budget)
        recent_months = [
            {"consumed_percent": 0.4},  # > 0.25
            {"consumed_percent": 0.35},
            {"consumed_percent": 0.3},
        ]

        credits = manager.calculate_recovery_credits(
            monthly_budget=1.0,
            recent_months_data=recent_months,
        )

        assert credits == 0.0

    def test_three_efficient_months(self):
        """Test recovery credits with 3 efficient months."""
        manager = BudgetCarryoverManager()

        # 3 efficient months (all consumed < 25% of budget)
        recent_months = [
            {"consumed_percent": 0.2},  # < 0.25
            {"consumed_percent": 0.15},
            {"consumed_percent": 0.1},
        ]

        credits = manager.calculate_recovery_credits(
            monthly_budget=1.0,
            recent_months_data=recent_months,
        )

        # 1.0 * 0.1 * 3 = 0.3
        assert credits == 0.3

    def test_year_end_bonus(self):
        """Test year-end recovery credit bonus."""
        manager = BudgetCarryoverManager()

        # 3 efficient months with year-end bonus
        recent_months = [
            {"consumed_percent": 0.2},
            {"consumed_percent": 0.15},
            {"consumed_percent": 0.1},
        ]

        credits = manager.calculate_recovery_credits(
            monthly_budget=1.0,
            recent_months_data=recent_months,
            is_year_end=True,
        )

        # 1.0 * 0.1 * 3 + 1.0 * 0.1 = 0.3 + 0.1 = 0.4
        assert credits == 0.4

    def test_max_lookback_months(self):
        """Test that only last 3 months are considered."""
        manager = BudgetCarryoverManager()

        # 5 efficient months (only 3 should count)
        recent_months = [
            {"consumed_percent": 0.2},
            {"consumed_percent": 0.15},
            {"consumed_percent": 0.1},
            {"consumed_percent": 0.2},
            {"consumed_percent": 0.15},
        ]

        credits = manager.calculate_recovery_credits(
            monthly_budget=1.0,
            recent_months_data=recent_months,
        )

        # Only first 3 months counted: 1.0 * 0.1 * 3 = 0.3
        assert credits == 0.3


class TestEffectiveBudget:
    """Test effective budget calculations."""

    def test_effective_budget_base_only(self):
        """Test effective budget with no carryover or credits."""
        manager = BudgetCarryoverManager()

        effective = manager.get_effective_budget(
            total_budget=0.5,
            carried_from_previous=0.0,
            recovery_credits=0.0,
        )

        assert effective == 0.5

    def test_effective_budget_with_carryover(self):
        """Test effective budget includes carryover."""
        manager = BudgetCarryoverManager()

        effective = manager.get_effective_budget(
            total_budget=0.5,
            carried_from_previous=0.2,
            recovery_credits=0.0,
        )

        assert effective == 0.7

    def test_effective_budget_with_recovery_credits(self):
        """Test effective budget includes recovery credits."""
        manager = BudgetCarryoverManager()

        effective = manager.get_effective_budget(
            total_budget=0.5,
            carried_from_previous=0.0,
            recovery_credits=0.1,
        )

        assert effective == 0.6

    def test_effective_budget_with_both(self):
        """Test effective budget with carryover and recovery credits."""
        manager = BudgetCarryoverManager()

        effective = manager.get_effective_budget(
            total_budget=0.5,
            carried_from_previous=0.2,
            recovery_credits=0.1,
        )

        assert effective == 0.8

    def test_consumption_percent_of_effective(self):
        """Test consumption percentage calculation."""
        manager = BudgetCarryoverManager()

        # Consumed 0.3% of effective budget 0.8%
        consumption_pct = manager.get_consumption_percent_of_effective(
            consumed=0.3,
            effective_budget=0.8,
        )

        # 0.3 / 0.8 * 100 = 37.5%
        assert consumption_pct == 37.5

    def test_consumption_percent_of_effective_full(self):
        """Test consumption percentage when budget fully consumed."""
        manager = BudgetCarryoverManager()

        # Consumed 0.8% of effective budget 0.8%
        consumption_pct = manager.get_consumption_percent_of_effective(
            consumed=0.8,
            effective_budget=0.8,
        )

        assert consumption_pct == 100.0

    def test_consumption_percent_of_effective_over(self):
        """Test consumption percentage when budget exceeded (capped at 100%)."""
        manager = BudgetCarryoverManager()

        # Consumed 0.9% of effective budget 0.8% (over)
        consumption_pct = manager.get_consumption_percent_of_effective(
            consumed=0.9,
            effective_budget=0.8,
        )

        # Should cap at 100%
        assert consumption_pct == 100.0


class TestCarryoverApplication:
    """Test carryover application to windows."""

    def test_apply_carryover_success(self):
        """Test successful carryover application."""
        manager = BudgetCarryoverManager()

        source = {
            "id": uuid4(),
            "total_budget_percent": 0.5,
            "consumed_percent": 0.2,
            "carried_over_to_next": 0.0,
            "is_carryover_locked": False,
        }
        target = {
            "id": uuid4(),
            "total_budget_percent": 0.5,
            "carried_over_from_previous": 0.0,
            "recovery_credits": 0.0,
        }

        result = manager.apply_carryover(source, target)

        assert result.success
        assert result.carried_amount == 0.3
        assert target["carried_over_from_previous"] == 0.3
        assert source["is_carryover_locked"] is True

    def test_year_boundary_carryover(self):
        """Test year boundary carryover application."""
        manager = BudgetCarryoverManager()

        source = {
            "id": uuid4(),
            "total_budget_percent": 0.5,
            "consumed_percent": 0.1,
            "carried_over_to_next": 0.0,
            "is_carryover_locked": False,
        }
        target = {
            "id": uuid4(),
            "total_budget_percent": 0.5,
            "carried_over_from_previous": 0.0,
            "recovery_credits": 0.0,
        }

        result = manager.handle_year_boundary(source, target)

        assert result.success
        assert result.carryover_type == "year_rollover"
        assert result.carried_amount == 0.4  # 100% of 0.4% unused


class TestCarryoverSummary:
    """Test carryover summary generation."""

    def test_carryover_summary_comprehensive(self):
        """Test comprehensive carryover summary."""
        manager = BudgetCarryoverManager()

        window = {
            "id": uuid4(),
            "total_budget_percent": 0.5,
            "consumed_percent": 0.3,
            "carried_over_from_previous": 0.2,
            "recovery_credits": 0.1,
            "total_available_budget": 0.8,
            "is_carryover_locked": False,
            "carryover_applied_at": None,
        }

        summary = manager.get_carryover_summary(window)

        assert summary["base_budget_percent"] == 0.5
        assert summary["consumed_percent"] == 0.3
        assert summary["carried_from_previous_percent"] == 0.2
        assert summary["recovery_credits_percent"] == 0.1
        assert summary["effective_budget_percent"] == 0.8
        assert summary["consumption_of_effective_percent"] == 37.5  # 0.3/0.8 * 100


class TestGlobalManager:
    """Test global carryover manager instance."""

    def test_singleton_pattern(self):
        """Test global manager is singleton."""
        manager1 = get_carryover_manager()
        manager2 = get_carryover_manager()

        assert manager1 is manager2


class TestIntegration:
    """Integration tests for carryover workflows."""

    def test_efficient_month_carryover_workflow(self):
        """Test complete workflow for efficient month with carryover."""
        manager = BudgetCarryoverManager()

        # Month 1: Consume 30% of 1.0% budget (high efficiency)
        month1 = {
            "id": uuid4(),
            "total_budget_percent": 1.0,
            "consumed_percent": 0.3,
        }

        carryover_amt = manager.calculate_carryover(1.0, 0.3)
        assert carryover_amt == 0.7  # 100% of 0.7% unused

        # Month 2: Apply carryover
        month2 = {
            "id": uuid4(),
            "total_budget_percent": 1.0,
            "consumed_percent": 0.0,
            "carried_over_from_previous": carryover_amt,
            "recovery_credits": 0.0,
        }

        effective = manager.get_effective_budget(1.0, carryover_amt, 0.0)
        assert effective == 1.7  # Budget + carryover

        # Month 2 can now consume up to 1.7% instead of 1.0%
        assert effective > 1.0

    def test_year_boundary_workflow(self):
        """Test complete year boundary workflow."""
        manager = BudgetCarryoverManager()

        # December: 10% consumption (high efficiency)
        december = {
            "id": uuid4(),
            "total_budget_percent": 1.0,
            "consumed_percent": 0.1,
        }

        # January: New month, no data yet
        january = {
            "id": uuid4(),
            "total_budget_percent": 1.0,
            "consumed_percent": 0.0,
            "carried_over_from_previous": 0.0,
            "recovery_credits": 0.0,
        }

        # Apply year boundary carryover
        result = manager.handle_year_boundary(december, january)

        assert result.success
        assert result.carryover_type == "year_rollover"
        assert january["carried_over_from_previous"] == 0.9  # 100% of 0.9% unused


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
