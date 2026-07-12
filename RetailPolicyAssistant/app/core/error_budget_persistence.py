"""Persistence integration for error budgets and user profiles."""

import asyncpg
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from app.core.error_budget import ErrorBudgetCalculator, get_error_budget_calculator
from app.core.user_slo_profiles import UserSLOProfileManager, get_user_slo_profile_manager
from app.repositories.error_budget_repo import (
    get_error_budget_repo,
    get_user_profile_repo,
)


class PersistentErrorBudgetManager:
    """Bridges in-memory error budget calculator with database storage."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize with database pool."""
        self.db_pool = db_pool
        self.budget_repo = get_error_budget_repo(db_pool)
        self.profile_repo = get_user_profile_repo(db_pool)
        self.budget_calc = get_error_budget_calculator()

    async def initialize_tenant_budget(
        self,
        month: str,
        tenant_id: Optional[str] = None,
        slo_percent: float = 99.5,
    ) -> Dict[str, Any]:
        """Initialize error budget for tenant month.

        Args:
            month: Month in "2026-07" format
            tenant_id: Optional tenant ID
            slo_percent: SLO percentage (99.5 = 0.5% budget)

        Returns:
            Budget window record
        """
        budget_percent = 100.0 - slo_percent

        # Create in database
        window = await self.budget_repo.create_budget_window(
            month=month,
            total_budget_percent=budget_percent,
            tenant_id=tenant_id,
        )

        return window

    async def record_error(
        self,
        month: str,
        error_type: str,
        severity: str,
        description: Optional[str] = None,
        query_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        route: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record error to both in-memory and persistent storage.

        Args:
            month: Month in "2026-07" format
            error_type: Type of error
            severity: Severity level
            description: Error description
            query_id: Associated query
            user_id: Associated user
            endpoint: API endpoint
            route: Query route
            tenant_id: Optional tenant ID

        Returns:
            Updated budget status
        """
        # Get or create budget window
        window = await self.budget_repo.get_budget_window(month, tenant_id)
        if not window:
            window = await self.initialize_tenant_budget(month, tenant_id)

        budget_window_id = window["id"]

        # Get severity weight (normal=1.0, high=1.5, critical=2.0)
        weights = {"normal": 1.0, "high": 1.5, "critical": 2.0}
        weight = weights.get(severity, 1.0)

        # Record in-memory
        self.budget_calc.add_error(error_type, severity)

        # Record to database
        await self.budget_repo.add_error_event(
            budget_window_id=budget_window_id,
            error_type=error_type,
            severity=severity,
            weight=weight,
            description=description,
            query_id=query_id,
            user_id=user_id,
            endpoint=endpoint,
            route=route,
        )

        # Get updated status
        status = self.budget_calc.get_budget_status()

        return {
            "budget_window_id": str(budget_window_id),
            "status": status,
            "event_recorded": True,
        }

    async def get_budget_status(
        self,
        month: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get budget status from database with burn rate analysis.

        Args:
            month: Month in "2026-07" format
            tenant_id: Optional tenant ID

        Returns:
            Budget status with database data
        """
        window = await self.budget_repo.get_budget_window(month, tenant_id)
        if not window:
            return {"error": "Budget window not found"}

        # Get burn rate
        burn_rate = await self.budget_repo.get_burn_rate_by_period(
            window["id"],
            period_minutes=60,
        )

        # Get recent errors
        errors = await self.budget_repo.get_window_errors(window["id"], limit=100)

        # Calculate status
        consumed = window.get("consumed_percent", 0)
        total = window.get("total_budget_percent", 0.5)
        remaining = max(0, total - consumed)

        status = "ok" if consumed < (total * 0.7) else "warning" if consumed < total else "exhausted"

        return {
            "month": month,
            "tenant_id": tenant_id,
            "total_budget_percent": total,
            "consumed_percent": consumed,
            "remaining_percent": remaining,
            "consumption_rate": (consumed / total * 100) if total > 0 else 0,
            "status": status,
            "burn_rate_analysis": {
                "last_hour_errors": burn_rate.get("error_count", 0),
                "hourly_weight": burn_rate.get("total_weight", 0),
            },
            "recent_errors_count": len(errors),
        }

    async def get_budget_history(
        self,
        month: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get budget history with snapshots.

        Args:
            month: Month in "2026-07" format
            tenant_id: Optional tenant ID

        Returns:
            Budget history data
        """
        window = await self.budget_repo.get_budget_window(month, tenant_id)
        if not window:
            return {"error": "Budget window not found"}

        # Get snapshots
        snapshots = await self.budget_repo.get_budget_history(window["id"], days=30)

        return {
            "month": month,
            "window_id": str(window["id"]),
            "snapshots": snapshots,
            "snapshot_count": len(snapshots),
        }

    async def create_daily_snapshot(
        self,
        month: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create daily budget snapshot.

        Args:
            month: Month in "2026-07" format
            tenant_id: Optional tenant ID

        Returns:
            Snapshot record
        """
        # Get current window
        window = await self.budget_repo.get_budget_window(month, tenant_id)
        if not window:
            window = await self.initialize_tenant_budget(month, tenant_id)

        consumed = window.get("consumed_percent", 0)
        total = window.get("total_budget_percent", 0.5)

        # Determine alert status
        if consumed >= total:
            alert_status = "exhausted"
        elif consumed >= (total * 0.8):
            alert_status = "critical"
        elif consumed >= (total * 0.5):
            alert_status = "warning"
        else:
            alert_status = "ok"

        # Calculate burn rate multiplier
        burn_rate_multiplier = 1.0  # Simplified for basic version
        if consumed > 0:
            # Estimate based on consumption pattern
            burn_rate_multiplier = (consumed / total) / 0.5  # Normalize to 0.5 period

        # Record snapshot
        snapshot = await self.budget_repo.create_budget_snapshot(
            budget_window_id=window["id"],
            consumed_percent=consumed,
            burn_rate_multiplier=burn_rate_multiplier,
            alert_status=alert_status,
        )

        return snapshot


class PersistentUserProfileManager:
    """Bridges in-memory user profile manager with database storage."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize with database pool."""
        self.db_pool = db_pool
        self.profile_repo = get_user_profile_repo(db_pool)
        self.profile_manager = get_user_slo_profile_manager()

    async def initialize_user_profile(
        self,
        user_id: str,
        tier: str,
    ) -> Dict[str, Any]:
        """Initialize user profile in database.

        Args:
            user_id: User identifier
            tier: User tier (trial, standard, premium, enterprise)

        Returns:
            User profile
        """
        # Get tier profile from in-memory manager
        profile = self.profile_manager.get_profile(user_id)

        # Store in database
        db_profile = await self.profile_repo.create_profile(
            user_id=user_id,
            tier=tier,
            latency_target_ms=profile.latency_target_ms,
            latency_hard_limit_ms=profile.latency_hard_limit_ms,
            latency_soft_warning_ms=profile.latency_soft_warning_ms,
            confidence_min=profile.confidence_min,
            confidence_escalate_threshold=profile.confidence_escalate_threshold,
            queries_per_hour=profile.queries_per_hour,
            queries_per_day=profile.queries_per_day,
            max_concurrent_queries=profile.max_concurrent_queries,
            availability_slo_percent=profile.availability_slo_percent,
            error_rate_max_percent=profile.error_rate_max_percent,
            allow_hybrid_routing=profile.allow_hybrid_routing,
            allow_sql_routing=profile.allow_sql_routing,
            allow_rag_routing=profile.allow_rag_routing,
            enable_caching=profile.enable_caching,
            enable_background_evaluation=profile.enable_background_evaluation,
            enable_circuit_breaker=profile.enable_circuit_breaker,
            enforce_hard_limits=profile.enforce_hard_limits,
            enforce_soft_limits=profile.enforce_soft_limits,
        )

        return db_profile

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile from database.

        Args:
            user_id: User identifier

        Returns:
            User profile
        """
        profile = await self.profile_repo.get_profile(user_id)

        if not profile:
            # Initialize default profile
            profile = await self.initialize_user_profile(user_id, "standard")

        return profile

    async def update_user_profile(
        self,
        user_id: str,
        **updates,
    ) -> Dict[str, Any]:
        """Update user profile in database.

        Args:
            user_id: User identifier
            **updates: Fields to update

        Returns:
            Updated profile
        """
        profile = await self.profile_repo.update_profile(user_id, **updates)
        return profile

    async def get_profiles_by_tier(self, tier: str) -> list:
        """Get all users of a tier.

        Args:
            tier: User tier

        Returns:
            List of profiles
        """
        profiles = await self.profile_repo.get_profiles_by_tier(tier)
        return profiles

    async def get_all_profiles(self, limit: int = 1000) -> list:
        """Get all user profiles.

        Args:
            limit: Maximum to return

        Returns:
            List of profiles
        """
        profiles = await self.profile_repo.get_all_profiles(limit)
        return profiles


# Global instances
_persistent_budget_mgr: Optional[PersistentErrorBudgetManager] = None
_persistent_profile_mgr: Optional[PersistentUserProfileManager] = None


def get_persistent_budget_manager(db_pool: asyncpg.Pool) -> PersistentErrorBudgetManager:
    """Get or create persistent budget manager."""
    global _persistent_budget_mgr
    if _persistent_budget_mgr is None or _persistent_budget_mgr.db_pool != db_pool:
        _persistent_budget_mgr = PersistentErrorBudgetManager(db_pool)
    return _persistent_budget_mgr


def get_persistent_profile_manager(db_pool: asyncpg.Pool) -> PersistentUserProfileManager:
    """Get or create persistent profile manager."""
    global _persistent_profile_mgr
    if _persistent_profile_mgr is None or _persistent_profile_mgr.db_pool != db_pool:
        _persistent_profile_mgr = PersistentUserProfileManager(db_pool)
    return _persistent_profile_mgr
