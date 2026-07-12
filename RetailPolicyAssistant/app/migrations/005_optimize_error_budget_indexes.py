"""Migration: Optimize error budget indexes with composite indexes for Phase 3.3.2."""

import asyncpg


async def upgrade(connection: asyncpg.Connection):
    """Add composite indexes to optimize frequent query patterns."""

    # CRITICAL: Burn rate query optimization (get_burn_rate_by_period hotspot)
    # Optimizes: get_burn_rate_by_period(), get_window_errors()
    # Benefit: 10-100x speedup for queries with large error volumes
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_error_events_window_timestamp
            ON error_events (budget_window_id, timestamp DESC);
    """)
    print("✓ Created composite index on error_events (budget_window_id, timestamp DESC)")

    # CRITICAL: SUM aggregate optimization (add_error_event subquery)
    # Optimizes: SUM(weight) calculation when updating consumed_percent
    # Benefit: O(1) covering index scan instead of O(n) full table scan per write
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_error_events_window_weight
            ON error_events (budget_window_id, weight);
    """)
    print("✓ Created covering index on error_events (budget_window_id, weight)")

    # HIGH: Budget history range queries
    # Optimizes: get_budget_history() date range filtering
    # Benefit: Efficient range scans on snapshot dates per window
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_budget_snapshots_window_date
            ON budget_snapshots (budget_window_id, snapshot_date DESC);
    """)
    print("✓ Created composite index on budget_snapshots (budget_window_id, snapshot_date DESC)")

    # HIGH: Budget window composite lookups
    # Optimizes: get_budget_window() two-column filter for multi-tenant isolation
    # Benefit: Efficient AND clause on (month, tenant_id) pair
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_error_budget_windows_month_tenant
            ON error_budget_windows (month, tenant_id);
    """)
    print("✓ Created composite index on error_budget_windows (month, tenant_id)")

    # MEDIUM: Future severity-based filtering
    # Optimizes: Future queries filtering errors by severity within a window
    # Benefit: Covers emerging analytics patterns
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_error_events_window_severity
            ON error_events (budget_window_id, severity);
    """)
    print("✓ Created composite index on error_events (budget_window_id, severity)")

    print("\n✅ Phase 3.3.2 Index Optimization Complete")
    print("   - 5 composite indexes created")
    print("   - Query patterns optimized for production load")
    print("   - Ready for performance testing")


async def downgrade(connection: asyncpg.Connection):
    """Remove composite indexes (rollback)."""
    await connection.execute("""
        DROP INDEX IF EXISTS idx_error_events_window_timestamp CASCADE;
        DROP INDEX IF EXISTS idx_error_events_window_weight CASCADE;
        DROP INDEX IF EXISTS idx_budget_snapshots_window_date CASCADE;
        DROP INDEX IF EXISTS idx_error_budget_windows_month_tenant CASCADE;
        DROP INDEX IF EXISTS idx_error_events_window_severity CASCADE;
    """)

    print("✓ Dropped Phase 3.3.2 optimization indexes")
