"""Migration: Add budget carryover and recovery credits support for Phase 3.3.3."""

import asyncpg


async def upgrade(connection: asyncpg.Connection):
    """Add carryover fields and audit table for budget management."""

    # Add new columns to error_budget_windows table
    await connection.execute("""
        ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
            carried_over_from_previous FLOAT DEFAULT 0.0;
    """)
    print("  [OK] Added carried_over_from_previous column")

    await connection.execute("""
        ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
            carried_over_to_next FLOAT DEFAULT 0.0;
    """)
    print("  [OK] Added carried_over_to_next column")

    await connection.execute("""
        ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
            recovery_credits FLOAT DEFAULT 0.0;
    """)
    print("  [OK] Added recovery_credits column")

    await connection.execute("""
        ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
            is_carryover_locked BOOLEAN DEFAULT FALSE;
    """)
    print("  [OK] Added is_carryover_locked column")

    await connection.execute("""
        ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
            carryover_applied_at TIMESTAMP NULL;
    """)
    print("  [OK] Added carryover_applied_at column")

    # Create computed column for total available budget
    # Note: Generated columns in PostgreSQL require the column to not already exist
    try:
        await connection.execute("""
            ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
                total_available_budget FLOAT
                GENERATED ALWAYS AS (total_budget_percent + carried_over_from_previous + recovery_credits) STORED;
        """)
        print("  [OK] Added total_available_budget generated column")
    except Exception as e:
        # If generated column not supported, create as regular column with default
        await connection.execute("""
            ALTER TABLE error_budget_windows ADD COLUMN IF NOT EXISTS
                total_available_budget FLOAT DEFAULT 0.0;
        """)
        print("  [OK] Added total_available_budget column (fallback)")

    # Create budget_carryover_events table (Audit trail)
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS budget_carryover_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Source and target windows
            source_window_id UUID NOT NULL REFERENCES error_budget_windows(id) ON DELETE CASCADE,
            target_window_id UUID NOT NULL REFERENCES error_budget_windows(id) ON DELETE CASCADE,

            -- Carryover details
            carried_amount FLOAT NOT NULL,
            carryover_type VARCHAR NOT NULL,  -- 'normal', 'recovery_credit', 'year_rollover'

            -- Metadata
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            applied_by VARCHAR DEFAULT 'system'
        );
    """)
    print("  [OK] Created budget_carryover_events table")

    # Create indexes for carryover event queries
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_carryover_events_source
            ON budget_carryover_events (source_window_id);
    """)
    print("  [OK] Created index on source_window_id")

    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_carryover_events_target
            ON budget_carryover_events (target_window_id);
    """)
    print("  [OK] Created index on target_window_id")

    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_carryover_events_type
            ON budget_carryover_events (carryover_type);
    """)
    print("  [OK] Created index on carryover_type")

    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_carryover_events_applied_at
            ON budget_carryover_events (applied_at);
    """)
    print("  [OK] Created index on applied_at")

    # Create composite index for efficient queries
    await connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_carryover_events_window_type
            ON budget_carryover_events (source_window_id, carryover_type);
    """)
    print("  [OK] Created composite index on source_window_id, carryover_type")

    print("\n[COMPLETE] Phase 3.3.3 Budget Carryover Schema Migration")
    print("   - 5 new columns added to error_budget_windows")
    print("   - budget_carryover_events audit table created")
    print("   - 5 optimized indexes created")
    print("   - Ready for carryover logic implementation")


async def downgrade(connection: asyncpg.Connection):
    """Remove carryover fields and audit table (rollback)."""

    # Drop indexes first
    await connection.execute("""
        DROP INDEX IF EXISTS idx_carryover_events_window_type CASCADE;
        DROP INDEX IF EXISTS idx_carryover_events_applied_at CASCADE;
        DROP INDEX IF EXISTS idx_carryover_events_type CASCADE;
        DROP INDEX IF EXISTS idx_carryover_events_target CASCADE;
        DROP INDEX IF EXISTS idx_carryover_events_source CASCADE;
    """)
    print("  [OK] Dropped carryover event indexes")

    # Drop audit table
    await connection.execute("""
        DROP TABLE IF EXISTS budget_carryover_events CASCADE;
    """)
    print("  [OK] Dropped budget_carryover_events table")

    # Drop columns from error_budget_windows
    await connection.execute("""
        ALTER TABLE error_budget_windows
            DROP COLUMN IF EXISTS total_available_budget,
            DROP COLUMN IF EXISTS carryover_applied_at,
            DROP COLUMN IF EXISTS is_carryover_locked,
            DROP COLUMN IF EXISTS recovery_credits,
            DROP COLUMN IF EXISTS carried_over_to_next,
            DROP COLUMN IF EXISTS carried_over_from_previous;
    """)
    print("  [OK] Dropped carryover columns from error_budget_windows")

    print("\n[COMPLETE] Phase 3.3.3 Budget Carryover Rollback")
    print("   - All carryover schema changes removed")
    print("   - Audit trail deleted")
    print("   - Original schema restored")
