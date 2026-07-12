"""Scheduled job for monthly budget carryover processing."""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from app.core.budget_carryover import BudgetCarryoverManager, CarryoverResult
from app.repositories.error_budget_repo import ErrorBudgetRepository


class MonthlyBudgetCarryoverJob:
    """Handles monthly budget carryover processing."""

    def __init__(self, db_pool=None):
        """Initialize carryover job.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.carryover_manager = BudgetCarryoverManager()
        self.results: List[CarryoverResult] = []
        self.errors: List[str] = []

    async def run(self, tenant_ids: List[str] = None) -> Dict[str, Any]:
        """Run monthly carryover for specified tenants.

        Args:
            tenant_ids: List of tenant IDs to process (None = all active)

        Returns:
            Job execution summary
        """
        if not self.db_pool:
            self.errors.append("Database pool not initialized")
            return self._get_summary()

        try:
            # Get previous and current month strings
            now = datetime.utcnow()
            current_month = f"{now.year:04d}-{now.month:02d}"

            # Calculate previous month
            if now.month == 1:
                prev_year = now.year - 1
                prev_month_num = 12
                is_year_boundary = True
            else:
                prev_year = now.year
                prev_month_num = now.month - 1
                is_year_boundary = False

            previous_month = f"{prev_year:04d}-{prev_month_num:02d}"

            # Get repository
            repo = ErrorBudgetRepository(self.db_pool)

            # If tenant_ids not specified, process all active tenants
            if not tenant_ids:
                tenant_ids = await self._get_active_tenants(repo)

            # Process each tenant
            for tenant_id in tenant_ids:
                try:
                    result = await self._process_tenant_carryover(
                        repo=repo,
                        previous_month=previous_month,
                        current_month=current_month,
                        tenant_id=tenant_id,
                        is_year_boundary=is_year_boundary,
                    )

                    if result:
                        self.results.append(result)

                except Exception as e:
                    error_msg = f"Tenant {tenant_id}: {str(e)}"
                    self.errors.append(error_msg)

            return self._get_summary()

        except Exception as e:
            self.errors.append(f"Job execution error: {str(e)}")
            return self._get_summary()

    async def _process_tenant_carryover(
        self,
        repo: ErrorBudgetRepository,
        previous_month: str,
        current_month: str,
        tenant_id: str,
        is_year_boundary: bool = False,
    ) -> CarryoverResult:
        """Process carryover for a single tenant.

        Args:
            repo: Error budget repository
            previous_month: Previous month string
            current_month: Current month string
            tenant_id: Tenant ID
            is_year_boundary: True if December→January transition

        Returns:
            CarryoverResult
        """
        # Get previous month's window
        source_window = await repo.get_budget_window_with_carryover(
            previous_month,
            tenant_id,
        )

        if not source_window:
            return None  # No previous month data, skip

        # Create or get current month's window
        target_window = await repo.get_budget_window_with_carryover(
            current_month,
            tenant_id,
        )

        if not target_window:
            # Create current month window
            target_window = await repo.create_budget_window(
                month=current_month,
                total_budget_percent=source_window.get("total_budget_percent", 0.5),
                tenant_id=tenant_id,
            )

        # Apply carryover
        if is_year_boundary:
            result = self.carryover_manager.handle_year_boundary(
                source_window,
                target_window,
            )
        else:
            result = self.carryover_manager.apply_carryover(
                source_window,
                target_window,
            )

        if result.success:
            # Persist carryover to database
            await repo.update_carryover_fields(
                window_id=target_window["id"],
                carried_from_previous=result.carried_amount,
                recovery_credits=target_window.get("recovery_credits", 0.0),
            )

            await repo.lock_window_for_carryover(source_window["id"])

            # Record audit event
            await repo.record_carryover_event(
                source_window_id=source_window["id"],
                target_window_id=target_window["id"],
                carried_amount=result.carried_amount,
                carryover_type=result.carryover_type,
                applied_by="system",
            )

        return result

    async def _get_active_tenants(self, repo: ErrorBudgetRepository) -> List[str]:
        """Get list of active tenants.

        Args:
            repo: Error budget repository

        Returns:
            List of tenant IDs
        """
        # For now, return empty list (would query active tenants from DB)
        # This is a placeholder for future tenant discovery
        return []

    def _get_summary(self) -> Dict[str, Any]:
        """Get job execution summary.

        Returns:
            Summary dict
        """
        return {
            "processed_count": len(self.results),
            "successful_count": sum(1 for r in self.results if r.success),
            "failed_count": sum(1 for r in self.results if not r.success),
            "errors": self.errors,
            "total_carried": sum(r.carried_amount for r in self.results if r.success),
            "executed_at": datetime.utcnow().isoformat(),
        }


async def run_monthly_carryover_job(db_pool, tenant_ids: List[str] = None) -> Dict[str, Any]:
    """Convenience function to run monthly carryover job.

    Args:
        db_pool: Database connection pool
        tenant_ids: Optional list of tenant IDs to process

    Returns:
        Job execution summary
    """
    job = MonthlyBudgetCarryoverJob(db_pool)
    return await job.run(tenant_ids)
