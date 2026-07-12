"""Error Budget Tracking & Management for SLO compliance.

Tracks monthly error budget, calculates burn rate, and provides alerts.
Used by Phase 3.2 for advanced SLO management.
Supports budget carryover from Phase 3.3.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import math
from app.core.budget_carryover import get_carryover_manager


@dataclass
class BudgetConfig:
    """Error budget configuration."""

    monthly_slo_percent: float = 99.5  # 99.5% SLO = 21.6 min/month budget
    daily_budget_percent: Optional[float] = None  # Auto-calculated if None
    alert_threshold_percent: float = 50.0  # Alert when 50% budget consumed
    critical_threshold_percent: float = 80.0  # Critical when 80% consumed
    burn_rate_threshold: float = 2.0  # Alert if burn rate > 2x expected

    def __post_init__(self):
        """Calculate daily budget if not provided."""
        if self.daily_budget_percent is None:
            # SLO 99.5% = 0.5% error budget = ~21.6 min/month
            # Spread across ~30 days
            monthly_error_percent = 100.0 - self.monthly_slo_percent
            self.daily_budget_percent = monthly_error_percent / 30.0


@dataclass
class ErrorEvent:
    """Single error event for budget consumption."""

    timestamp: datetime
    error_type: str  # 'latency', 'error', 'availability'
    severity: str = "normal"  # 'normal', 'high', 'critical'
    description: str = ""
    weight: float = 1.0  # Multiplier for budget impact (critical = 2.0x)


@dataclass
class BudgetWindow:
    """Monthly error budget window."""

    month: str  # "2026-07" format
    total_budget_percent: float = field(init=False)
    consumed_percent: float = 0.0
    errors: list = field(default_factory=list)
    start_date: datetime = field(default_factory=lambda: datetime.utcnow().replace(day=1))
    end_date: datetime = field(init=False)
    # Carryover fields
    carried_over_from_previous: float = 0.0
    recovery_credits: float = 0.0

    def __post_init__(self):
        """Initialize window dates."""
        # End of current month
        if self.start_date.month == 12:
            self.end_date = self.start_date.replace(year=self.start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            self.end_date = self.start_date.replace(month=self.start_date.month + 1, day=1) - timedelta(days=1)

    def get_effective_budget(self) -> float:
        """Get total effective budget including carryover and recovery credits.

        Returns:
            Effective budget percent
        """
        return self.total_budget_percent + self.carried_over_from_previous + self.recovery_credits

    def get_remaining_effective(self) -> float:
        """Get remaining effective budget.

        Returns:
            Remaining effective budget percent
        """
        effective = self.get_effective_budget()
        return max(0.0, effective - self.consumed_percent)

        # SLO 99.5% = 0.5% error budget
        self.total_budget_percent = 100.0 - 99.5

    def add_error(self, error: ErrorEvent):
        """Add error to window."""
        self.errors.append(error)
        self._recalculate_consumption()

    def _recalculate_consumption(self):
        """Recalculate total budget consumption."""
        total_weight = sum(e.weight for e in self.errors)
        self.consumed_percent = min(100.0, total_weight)  # Cap at 100%

    def remaining_percent(self) -> float:
        """Get remaining budget percentage."""
        return max(0.0, self.total_budget_percent - self.consumed_percent)

    def is_exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return self.consumed_percent >= self.total_budget_percent


class ErrorBudgetCalculator:
    """Calculate and track error budget."""

    def __init__(self, config: Optional[BudgetConfig] = None):
        """Initialize budget calculator.

        Args:
            config: Optional custom configuration
        """
        self.config = config or BudgetConfig()
        self.windows: Dict[str, BudgetWindow] = {}
        self.current_window: Optional[BudgetWindow] = None

    def get_current_window(self) -> BudgetWindow:
        """Get or create current month window."""
        now = datetime.utcnow()
        month_key = now.strftime("%Y-%m")

        if month_key not in self.windows:
            self.windows[month_key] = BudgetWindow(month=month_key)

        self.current_window = self.windows[month_key]
        return self.current_window

    def add_error(self, error_type: str, severity: str = "normal", description: str = ""):
        """Add error event to current budget window.

        Args:
            error_type: Type of error ('latency', 'error', 'availability')
            severity: Severity level ('normal', 'high', 'critical')
            description: Error description
        """
        window = self.get_current_window()

        # Calculate weight based on severity
        weight = {
            "normal": 1.0,
            "high": 1.5,
            "critical": 2.0,
        }.get(severity, 1.0)

        error = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_type=error_type,
            severity=severity,
            description=description,
            weight=weight,
        )

        window.add_error(error)

    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status including carryover information.

        Returns:
            {
                "month": "2026-07",
                "total_budget_percent": 0.5,
                "carried_from_previous_percent": 0.2,
                "recovery_credits_percent": 0.1,
                "effective_budget_percent": 0.8,
                "consumed_percent": 0.35,
                "remaining_percent": 0.15,
                "remaining_effective_percent": 0.45,
                "consumption_rate": 35.0,  # % of base budget
                "consumption_of_effective_rate": 43.75,  # % of effective budget
                "days_in_month": 31,
                "days_elapsed": 12,
                "expected_daily_burn": 0.016,  # base / 30 days
                "actual_daily_burn": 0.029,  # consumed / days_elapsed
                "burn_rate_multiplier": 1.8,  # actual / expected
                "exhaustion_date": "2026-07-25",  # Predicted date
                "status": "warning",  # ok, warning, critical, exhausted
                "alert": False,
                "alert_reason": "",
                "carryover_info": {
                    "has_carryover": True,
                    "has_recovery_credits": True,
                    "entering_carryover_budget": False,
                }
            }
        """
        window = self.get_current_window()
        now = datetime.utcnow()

        days_in_month = (window.end_date - window.start_date).days + 1
        days_elapsed = (now - window.start_date).days + 1
        days_remaining = days_in_month - days_elapsed

        # Calculate effective budget (includes carryover and recovery credits)
        effective_budget = window.get_effective_budget()
        remaining_effective = window.get_remaining_effective()

        expected_daily_burn = window.total_budget_percent / days_in_month
        actual_daily_burn = window.consumed_percent / days_elapsed if days_elapsed > 0 else 0
        burn_rate = actual_daily_burn / expected_daily_burn if expected_daily_burn > 0 else 0

        # Predict exhaustion date using effective budget
        if actual_daily_burn > 0:
            days_to_exhaustion = remaining_effective / actual_daily_burn
            exhaustion_date = now + timedelta(days=days_to_exhaustion)
        else:
            exhaustion_date = window.end_date

        # Determine status based on effective budget
        consumption_rate_base = window.consumed_percent / window.total_budget_percent * 100 if window.total_budget_percent > 0 else 0
        consumption_rate_effective = window.consumed_percent / effective_budget * 100 if effective_budget > 0 else 0

        is_exhausted_effective = window.consumed_percent >= effective_budget
        entering_carryover = window.consumed_percent > window.total_budget_percent

        if is_exhausted_effective:
            status = "exhausted"
        elif consumption_rate_effective >= self.config.critical_threshold_percent:
            status = "critical"
        elif consumption_rate_effective >= self.config.alert_threshold_percent:
            status = "warning"
        else:
            status = "ok"

        alert = False
        alert_reason = ""

        if burn_rate > self.config.burn_rate_threshold:
            alert = True
            alert_reason = f"High burn rate: {burn_rate:.1f}x expected"

        if is_exhausted_effective:
            alert = True
            alert_reason = "Error budget (including carryover) exhausted"

        if entering_carryover:
            alert = True
            alert_reason = "Consuming carryover budget"

        # Get carryover manager for summary
        carryover_mgr = get_carryover_manager()
        carryover_summary = carryover_mgr.get_carryover_summary({
            "total_budget_percent": window.total_budget_percent,
            "consumed_percent": window.consumed_percent,
            "carried_over_from_previous": window.carried_over_from_previous,
            "recovery_credits": window.recovery_credits,
            "total_available_budget": effective_budget,
        })

        return {
            "month": window.month,
            "total_budget_percent": round(window.total_budget_percent, 4),
            "carried_from_previous_percent": round(window.carried_over_from_previous, 4),
            "recovery_credits_percent": round(window.recovery_credits, 4),
            "effective_budget_percent": round(effective_budget, 4),
            "consumed_percent": round(window.consumed_percent, 4),
            "remaining_percent": round(window.remaining_percent(), 4),
            "remaining_effective_percent": round(remaining_effective, 4),
            "consumption_rate": round(consumption_rate_base, 2),
            "consumption_of_effective_rate": round(consumption_rate_effective, 2),
            "days_in_month": days_in_month,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "expected_daily_burn": round(expected_daily_burn, 6),
            "actual_daily_burn": round(actual_daily_burn, 6),
            "burn_rate_multiplier": round(burn_rate, 2),
            "exhaustion_date": exhaustion_date.strftime("%Y-%m-%d"),
            "status": status,
            "alert": alert,
            "alert_reason": alert_reason,
            "carryover_info": {
                "has_carryover": window.carried_over_from_previous > 0.0,
                "has_recovery_credits": window.recovery_credits > 0.0,
                "entering_carryover_budget": entering_carryover,
            }
        }

    def get_burn_rate_analysis(self) -> Dict[str, Any]:
        """Get detailed burn rate analysis.

        Returns:
            Hourly, daily, and weekly burn rates
        """
        window = self.get_current_window()
        now = datetime.utcnow()

        # Analyze errors by time period
        hourly_errors = {"last_hour": 0, "last_24h": 0}
        daily_errors = {"last_day": 0, "last_7d": 0}

        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        for error in window.errors:
            if error.timestamp >= hour_ago:
                hourly_errors["last_hour"] += error.weight
            if error.timestamp >= day_ago:
                hourly_errors["last_24h"] += error.weight
            if error.timestamp >= day_ago:
                daily_errors["last_day"] += error.weight
            if error.timestamp >= week_ago:
                daily_errors["last_7d"] += error.weight

        return {
            "period_analysis": {
                "last_hour_errors": round(hourly_errors["last_hour"], 2),
                "last_24h_errors": round(hourly_errors["last_24h"], 2),
                "last_7d_errors": round(daily_errors["last_7d"], 2),
            },
            "error_types": self._analyze_error_types(),
            "severity_distribution": self._analyze_severity(),
        }

    def _analyze_error_types(self) -> Dict[str, int]:
        """Analyze errors by type."""
        window = self.get_current_window()
        types = {}
        for error in window.errors:
            types[error.error_type] = types.get(error.error_type, 0) + 1
        return types

    def _analyze_severity(self) -> Dict[str, int]:
        """Analyze errors by severity."""
        window = self.get_current_window()
        severity = {}
        for error in window.errors:
            severity[error.severity] = severity.get(error.severity, 0) + 1
        return severity

    def get_recovery_plan(self) -> Dict[str, Any]:
        """Get recovery plan if budget is at risk.

        Returns:
            Actions to reduce burn rate
        """
        status = self.get_budget_status()

        if status["status"] == "ok":
            return {
                "status": "healthy",
                "actions": [],
                "recommendation": "No action needed",
            }

        actions = []

        if status["burn_rate_multiplier"] > 2.0:
            actions.append({
                "priority": "critical",
                "action": "Reduce query load",
                "description": "Burn rate is 2x+ expected. Consider rate limiting or request admission control.",
                "impact": f"Could save {status['remaining_percent'] / 2 * 100:.1f}% of budget",
            })

        if status["burn_rate_multiplier"] > 1.5:
            actions.append({
                "priority": "high",
                "action": "Optimize performance",
                "description": "Implement latency optimizations to reduce SLO breaches.",
                "impact": f"Could save ~{status['remaining_percent'] / 4 * 100:.1f}% of budget",
            })

        if status["status"] == "critical":
            actions.append({
                "priority": "high",
                "action": "Enable graceful degradation",
                "description": "Switch to simpler query routes to reduce errors.",
                "impact": f"Could extend budget by {status['days_remaining']} more days",
            })

        if status["status"] == "exhausted":
            actions.append({
                "priority": "emergency",
                "action": "Enable circuit breaker",
                "description": "Reject low-priority requests to preserve budget.",
                "impact": "Protects critical functionality",
            })

        return {
            "status": status["status"],
            "actions": actions,
            "recommendation": self._get_recommendation(status),
        }

    def _get_recommendation(self, status: Dict[str, Any]) -> str:
        """Get recommendation based on status."""
        if status["status"] == "exhausted":
            return "ERROR BUDGET EXHAUSTED. Enable circuit breaker immediately."
        elif status["status"] == "critical":
            return "Budget at critical level. Implement performance optimizations."
        elif status["status"] == "warning":
            return "Budget consumption accelerating. Monitor closely."
        else:
            return "Budget on track. Continue monitoring."

    def reset_window(self, month: str):
        """Reset a specific month window (for testing).

        Args:
            month: Month in "2026-07" format
        """
        if month in self.windows:
            del self.windows[month]


# Global instance
_error_budget_calculator: Optional[ErrorBudgetCalculator] = None


def get_error_budget_calculator(config: Optional[BudgetConfig] = None) -> ErrorBudgetCalculator:
    """Get or create global error budget calculator."""
    global _error_budget_calculator
    if _error_budget_calculator is None:
        _error_budget_calculator = ErrorBudgetCalculator(config)
    return _error_budget_calculator


def record_slo_error(error_type: str, severity: str = "normal", description: str = ""):
    """Record an SLO error to the budget.

    Args:
        error_type: Type of error ('latency', 'error', 'availability')
        severity: Severity ('normal', 'high', 'critical')
        description: Error description
    """
    calculator = get_error_budget_calculator()
    calculator.add_error(error_type, severity, description)
