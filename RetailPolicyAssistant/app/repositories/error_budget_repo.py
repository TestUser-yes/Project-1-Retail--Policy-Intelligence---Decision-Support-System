"""Repository for error budget persistence."""

import asyncpg
from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any


class ErrorBudgetRepository:
    """Manages error budget storage and queries."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize repository with database pool."""
        self.db_pool = db_pool

    async def create_budget_window(
        self,
        month: str,
        total_budget_percent: float,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new error budget window.

        Args:
            month: Month in "2026-07" format
            total_budget_percent: Total budget percent (0.5 for 99.5% SLO)
            tenant_id: Optional tenant ID for multi-tenancy

        Returns:
            Created window record
        """
        # Parse month to dates
        year, month_num = month.split("-")
        start_date = datetime(int(year), int(month_num), 1).date()

        # Calculate end date
        if int(month_num) == 12:
            end_date = datetime(int(year) + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(int(year), int(month_num) + 1, 1).date() - timedelta(days=1)

        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO error_budget_windows (
                    month, tenant_id, total_budget_percent, start_date, end_date
                ) VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (month, tenant_id) DO UPDATE
                SET updated_at = CURRENT_TIMESTAMP
                RETURNING id, month, total_budget_percent, consumed_percent;
            """, month, tenant_id, total_budget_percent, start_date, end_date)

        return dict(result) if result else {}

    async def add_error_event(
        self,
        budget_window_id: UUID,
        error_type: str,
        severity: str,
        weight: float,
        description: Optional[str] = None,
        query_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        route: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an error event to a budget window.

        Args:
            budget_window_id: ID of budget window
            error_type: Type of error ('latency', 'error', 'availability')
            severity: Severity level ('normal', 'high', 'critical')
            weight: Weight multiplier (1.0-2.0)
            description: Error description
            query_id: Associated query ID
            user_id: Associated user ID
            endpoint: API endpoint
            route: Query route

        Returns:
            Created event record
        """
        async with self.db_pool.acquire() as conn:
            # Insert event
            result = await conn.fetchrow("""
                INSERT INTO error_events (
                    budget_window_id, error_type, severity, weight, description,
                    query_id, user_id, endpoint, route
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id, timestamp;
            """, budget_window_id, error_type, severity, weight, description,
                query_id, user_id, endpoint, route)

            # Update window consumed percentage
            await conn.execute("""
                UPDATE error_budget_windows
                SET consumed_percent = (
                    SELECT SUM(weight) FROM error_events
                    WHERE budget_window_id = $1
                )
                WHERE id = $1;
            """, budget_window_id)

            return dict(result) if result else {}

    async def get_budget_window(
        self,
        month: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get error budget window for month.

        Args:
            month: Month in "2026-07" format
            tenant_id: Optional tenant ID

        Returns:
            Budget window record
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT * FROM error_budget_windows
                WHERE month = $1 AND tenant_id IS NOT DISTINCT FROM $2;
            """, month, tenant_id)

        return dict(result) if result else {}

    async def get_window_errors(
        self,
        budget_window_id: UUID,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get all errors in a budget window.

        Args:
            budget_window_id: ID of budget window
            limit: Maximum number of errors

        Returns:
            List of error records
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM error_events
                WHERE budget_window_id = $1
                ORDER BY timestamp DESC
                LIMIT $2;
            """, budget_window_id, limit)

        return [dict(row) for row in rows]

    async def get_burn_rate_by_period(
        self,
        budget_window_id: UUID,
        period_minutes: int = 60,
    ) -> Dict[str, Any]:
        """Get burn rate for a time period.

        Args:
            budget_window_id: ID of budget window
            period_minutes: Period in minutes

        Returns:
            Burn rate analysis
        """
        cutoff = datetime.utcnow() - timedelta(minutes=period_minutes)

        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT
                    COUNT(*) as error_count,
                    SUM(weight) as total_weight,
                    AVG(weight) as avg_weight
                FROM error_events
                WHERE budget_window_id = $1 AND timestamp >= $2;
            """, budget_window_id, cutoff)

        return dict(result) if result else {"error_count": 0, "total_weight": 0}

    async def create_budget_snapshot(
        self,
        budget_window_id: UUID,
        consumed_percent: float,
        burn_rate_multiplier: float,
        alert_status: str,
    ) -> Dict[str, Any]:
        """Create daily budget snapshot.

        Args:
            budget_window_id: ID of budget window
            consumed_percent: Current consumption
            burn_rate_multiplier: Burn rate multiplier
            alert_status: Alert status

        Returns:
            Created snapshot
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO budget_snapshots (
                    budget_window_id, snapshot_date, consumed_percent,
                    burn_rate_multiplier, alert_status
                ) VALUES ($1, CURRENT_DATE, $2, $3, $4)
                RETURNING id, snapshot_date;
            """, budget_window_id, consumed_percent, burn_rate_multiplier, alert_status)

        return dict(result) if result else {}

    async def get_budget_history(
        self,
        budget_window_id: UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get budget snapshot history.

        Args:
            budget_window_id: ID of budget window
            days: Number of days to retrieve

        Returns:
            List of snapshots
        """
        cutoff = datetime.utcnow().date() - timedelta(days=days)

        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM budget_snapshots
                WHERE budget_window_id = $1 AND snapshot_date >= $2
                ORDER BY snapshot_date DESC;
            """, budget_window_id, cutoff)

        return [dict(row) for row in rows]


class UserProfileRepository:
    """Manages user SLO profile storage."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize repository with database pool."""
        self.db_pool = db_pool

    async def create_profile(
        self,
        user_id: str,
        tier: str,
        latency_target_ms: float,
        latency_hard_limit_ms: float,
        latency_soft_warning_ms: float,
        confidence_min: float,
        confidence_escalate_threshold: float,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create or update user SLO profile.

        Args:
            user_id: User identifier
            tier: User tier (trial, standard, premium, enterprise)
            latency_target_ms: Target latency
            latency_hard_limit_ms: Hard limit latency
            latency_soft_warning_ms: Soft warning latency
            confidence_min: Minimum confidence
            confidence_escalate_threshold: Escalation threshold
            **kwargs: Additional profile fields

        Returns:
            Created profile
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO user_slo_profiles (
                    user_id, tier, latency_target_ms, latency_hard_limit_ms,
                    latency_soft_warning_ms, confidence_min, confidence_escalate_threshold,
                    queries_per_hour, queries_per_day, max_concurrent_queries,
                    availability_slo_percent, error_rate_max_percent,
                    allow_hybrid_routing, allow_sql_routing, allow_rag_routing,
                    enable_caching, enable_background_evaluation, enable_circuit_breaker,
                    enforce_hard_limits, enforce_soft_limits, is_custom
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, TRUE
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    tier = $2, latency_target_ms = $3, updated_at = CURRENT_TIMESTAMP
                RETURNING id, user_id, tier;
            """, user_id, tier, latency_target_ms, latency_hard_limit_ms,
                latency_soft_warning_ms, confidence_min, confidence_escalate_threshold,
                kwargs.get('queries_per_hour'), kwargs.get('queries_per_day'),
                kwargs.get('max_concurrent_queries'), kwargs.get('availability_slo_percent', 99.5),
                kwargs.get('error_rate_max_percent', 1.0),
                kwargs.get('allow_hybrid_routing', True), kwargs.get('allow_sql_routing', True),
                kwargs.get('allow_rag_routing', True), kwargs.get('enable_caching', True),
                kwargs.get('enable_background_evaluation', False), kwargs.get('enable_circuit_breaker', False),
                kwargs.get('enforce_hard_limits', True), kwargs.get('enforce_soft_limits', True))

        return dict(result) if result else {}

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user SLO profile.

        Args:
            user_id: User identifier

        Returns:
            User profile
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT * FROM user_slo_profiles WHERE user_id = $1;
            """, user_id)

        return dict(result) if result else {}

    async def update_profile(self, user_id: str, **updates) -> Dict[str, Any]:
        """Update user profile fields.

        Args:
            user_id: User identifier
            **updates: Fields to update

        Returns:
            Updated profile
        """
        set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
        values = [user_id] + list(updates.values())

        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow(f"""
                UPDATE user_slo_profiles
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $1
                RETURNING id, user_id, tier;
            """, *values)

        return dict(result) if result else {}

    async def get_profiles_by_tier(self, tier: str) -> List[Dict[str, Any]]:
        """Get all profiles of a specific tier.

        Args:
            tier: User tier

        Returns:
            List of profiles
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM user_slo_profiles WHERE tier = $1;
            """, tier)

        return [dict(row) for row in rows]

    async def get_all_profiles(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all user profiles.

        Args:
            limit: Maximum number to return

        Returns:
            List of profiles
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM user_slo_profiles LIMIT $1;
            """, limit)

        return [dict(row) for row in rows]


# Global instances
_budget_repo: Optional[ErrorBudgetRepository] = None
_profile_repo: Optional[UserProfileRepository] = None


def get_error_budget_repo(db_pool: asyncpg.Pool) -> ErrorBudgetRepository:
    """Get or create error budget repository."""
    global _budget_repo
    if _budget_repo is None or _budget_repo.db_pool != db_pool:
        _budget_repo = ErrorBudgetRepository(db_pool)
    return _budget_repo


def get_user_profile_repo(db_pool: asyncpg.Pool) -> UserProfileRepository:
    """Get or create user profile repository."""
    global _profile_repo
    if _profile_repo is None or _profile_repo.db_pool != db_pool:
        _profile_repo = UserProfileRepository(db_pool)
    return _profile_repo
