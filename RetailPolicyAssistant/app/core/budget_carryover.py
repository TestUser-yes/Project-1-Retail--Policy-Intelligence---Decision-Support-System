"""Budget carryover logic for multi-month SLO management."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


@dataclass
class CarryoverResult:
    """Result of a carryover operation."""

    source_window_id: UUID
    target_window_id: UUID
    carried_amount: float
    carryover_type: str  # 'normal', 'recovery_credit', 'year_rollover'
    applied_at: datetime
    success: bool = True
    error_message: Optional[str] = None


class BudgetCarryoverManager:
    """Manages error budget carryover across months."""

    # Configuration constants
    MAX_CARRYOVER_MULTIPLIER = 1.0  # Max carryover = 1x monthly budget
    EFFICIENCY_THRESHOLD_HIGH = 0.50  # < 50% consumption = high efficiency
    EFFICIENCY_THRESHOLD_MED = 0.80  # 50-80% consumption = medium efficiency
    CARRYOVER_RATE_HIGH = 1.0  # 100% of unused for high efficiency
    CARRYOVER_RATE_MED = 0.5  # 50% of unused for medium efficiency
    CARRYOVER_RATE_LOW = 0.0  # 0% of unused for low efficiency
    RECOVERY_CREDIT_PER_MONTH = 0.1  # 10% of budget per efficient month
    RECOVERY_CREDIT_MAX_MONTHS = 3  # Look back 3 months max
    RECOVERY_CREDIT_YEAR_END_BONUS = 0.1  # Extra 10% on Jan 1st
    EFFICIENT_MONTH_THRESHOLD = 0.25  # < 25% consumption = efficient

    def calculate_carryover(
        self,
        monthly_budget: float,
        consumed_percent: float,
    ) -> float:
        """Calculate carryover amount based on consumption efficiency.

        Args:
            monthly_budget: Monthly budget percent (e.g., 0.5 for 99.5% SLO)
            consumed_percent: Actual consumption percent

        Returns:
            Amount to carry over (float)

        Examples:
            - Budget 0.5%, consumed 0.2% (40% used) → carry 0.3 * 1.0 = 0.3%
            - Budget 0.5%, consumed 0.3% (60% used) → carry 0.2 * 0.5 = 0.1%
            - Budget 0.5%, consumed 0.45% (90% used) → carry 0.05 * 0.0 = 0.0%
        """
        if consumed_percent >= monthly_budget:
            # Budget exhausted or over
            return 0.0

        # Calculate unused budget
        unused = monthly_budget - consumed_percent

        # Determine carryover rate based on efficiency
        consumption_ratio = consumed_percent / monthly_budget

        if consumption_ratio < self.EFFICIENCY_THRESHOLD_HIGH:
            # High efficiency: carry over 100% of unused
            carryover_rate = self.CARRYOVER_RATE_HIGH
        elif consumption_ratio < self.EFFICIENCY_THRESHOLD_MED:
            # Medium efficiency: carry over 50% of unused
            carryover_rate = self.CARRYOVER_RATE_MED
        else:
            # Low efficiency: carry over 0% of unused
            carryover_rate = self.CARRYOVER_RATE_LOW

        # Calculate carryover amount
        carryover = unused * carryover_rate

        # Apply maximum carryover cap (1x monthly budget)
        max_carryover = monthly_budget * self.MAX_CARRYOVER_MULTIPLIER
        carryover = min(carryover, max_carryover)

        return round(carryover, 6)  # 6 decimal places for precision

    def apply_carryover(
        self,
        source_window: Dict[str, Any],
        target_window: Dict[str, Any],
    ) -> CarryoverResult:
        """Apply carryover from source month to target month.

        Args:
            source_window: Source budget window dict
            target_window: Target budget window dict (should exist)

        Returns:
            CarryoverResult with success status
        """
        try:
            # Calculate carryover amount
            carryover_amount = self.calculate_carryover(
                source_window["total_budget_percent"],
                source_window["consumed_percent"],
            )

            # Apply to target window
            target_window["carried_over_from_previous"] = carryover_amount
            target_window["total_available_budget"] = (
                target_window["total_budget_percent"]
                + carryover_amount
                + target_window.get("recovery_credits", 0.0)
            )

            # Mark source as locked
            source_window["carried_over_to_next"] = carryover_amount
            source_window["is_carryover_locked"] = True
            source_window["carryover_applied_at"] = datetime.utcnow()

            return CarryoverResult(
                source_window_id=source_window["id"],
                target_window_id=target_window["id"],
                carried_amount=carryover_amount,
                carryover_type="normal",
                applied_at=datetime.utcnow(),
                success=True,
            )
        except Exception as e:
            return CarryoverResult(
                source_window_id=source_window["id"],
                target_window_id=target_window["id"],
                carried_amount=0.0,
                carryover_type="normal",
                applied_at=datetime.utcnow(),
                success=False,
                error_message=str(e),
            )

    def handle_year_boundary(
        self,
        source_window: Dict[str, Any],
        target_window: Dict[str, Any],
    ) -> CarryoverResult:
        """Handle December → January year boundary transition.

        Args:
            source_window: December window
            target_window: January window

        Returns:
            CarryoverResult marked as year_rollover
        """
        try:
            # Calculate standard carryover
            carryover_amount = self.calculate_carryover(
                source_window["total_budget_percent"],
                source_window["consumed_percent"],
            )

            # Apply to target window
            target_window["carried_over_from_previous"] = carryover_amount
            target_window["total_available_budget"] = (
                target_window["total_budget_percent"]
                + carryover_amount
                + target_window.get("recovery_credits", 0.0)
            )

            # Mark source as locked
            source_window["carried_over_to_next"] = carryover_amount
            source_window["is_carryover_locked"] = True
            source_window["carryover_applied_at"] = datetime.utcnow()

            return CarryoverResult(
                source_window_id=source_window["id"],
                target_window_id=target_window["id"],
                carried_amount=carryover_amount,
                carryover_type="year_rollover",  # Mark as year boundary
                applied_at=datetime.utcnow(),
                success=True,
            )
        except Exception as e:
            return CarryoverResult(
                source_window_id=source_window["id"],
                target_window_id=target_window["id"],
                carried_amount=0.0,
                carryover_type="year_rollover",
                applied_at=datetime.utcnow(),
                success=False,
                error_message=str(e),
            )

    def calculate_recovery_credits(
        self,
        monthly_budget: float,
        recent_months_data: List[Dict[str, float]],
        is_year_end: bool = False,
    ) -> float:
        """Calculate recovery credits based on efficient prior months.

        Args:
            monthly_budget: Monthly budget percent
            recent_months_data: List of dicts with 'consumed_percent' for recent months
            is_year_end: True if this is Jan 1st (year-end bonus)

        Returns:
            Recovery credits amount (float)

        Example:
            - Budget 0.5%, 3 efficient prior months → 0.5 * 0.1 * 3 = 0.15%
            - On Jan 1st with 3 efficient → 0.5 * (0.1 * 3 + 0.1) = 0.2%
        """
        if not recent_months_data:
            return 0.0

        # Count efficient months (< 25% consumption)
        efficient_months = 0
        for month_data in recent_months_data[:self.RECOVERY_CREDIT_MAX_MONTHS]:
            consumed = month_data.get("consumed_percent", 0.0)
            if consumed < (monthly_budget * self.EFFICIENT_MONTH_THRESHOLD):
                efficient_months += 1

        # Calculate recovery credits
        credits = monthly_budget * self.RECOVERY_CREDIT_PER_MONTH * efficient_months

        # Add year-end bonus on January 1st
        if is_year_end and efficient_months > 0:
            credits += monthly_budget * self.RECOVERY_CREDIT_YEAR_END_BONUS

        return round(credits, 6)

    def get_effective_budget(
        self,
        total_budget: float,
        carried_from_previous: float,
        recovery_credits: float,
    ) -> float:
        """Calculate effective budget including carryover and recovery credits.

        Args:
            total_budget: Base monthly budget
            carried_from_previous: Carryover from prior month
            recovery_credits: Recovery credits available

        Returns:
            Total effective budget
        """
        effective = total_budget + carried_from_previous + recovery_credits
        return round(effective, 6)

    def get_consumption_percent_of_effective(
        self,
        consumed: float,
        effective_budget: float,
    ) -> float:
        """Calculate consumption percentage of effective budget.

        Args:
            consumed: Amount consumed
            effective_budget: Total effective budget

        Returns:
            Consumption as percent (0-100)
        """
        if effective_budget == 0.0:
            return 0.0

        consumption_pct = (consumed / effective_budget) * 100.0
        return round(min(consumption_pct, 100.0), 2)

    def get_carryover_summary(
        self,
        window: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get comprehensive carryover summary for a window.

        Args:
            window: Budget window dict

        Returns:
            Summary dict
        """
        total_budget = window.get("total_budget_percent", 0.0)
        consumed = window.get("consumed_percent", 0.0)
        carried_from_prev = window.get("carried_over_from_previous", 0.0)
        recovery_credits = window.get("recovery_credits", 0.0)
        effective_budget = window.get("total_available_budget", 0.0)

        if effective_budget == 0.0:
            effective_budget = self.get_effective_budget(total_budget, carried_from_prev, recovery_credits)

        consumption_of_effective = self.get_consumption_percent_of_effective(consumed, effective_budget)

        return {
            "base_budget_percent": total_budget,
            "consumed_percent": consumed,
            "carried_from_previous_percent": carried_from_prev,
            "recovery_credits_percent": recovery_credits,
            "effective_budget_percent": effective_budget,
            "consumption_of_base_percent": (consumed / total_budget * 100.0) if total_budget > 0 else 0.0,
            "consumption_of_effective_percent": consumption_of_effective,
            "is_carryover_locked": window.get("is_carryover_locked", False),
            "carryover_applied_at": window.get("carryover_applied_at"),
        }


# Global instance
_carryover_manager: Optional[BudgetCarryoverManager] = None


def get_carryover_manager() -> BudgetCarryoverManager:
    """Get or create global carryover manager."""
    global _carryover_manager
    if _carryover_manager is None:
        _carryover_manager = BudgetCarryoverManager()
    return _carryover_manager
