"""Migration: Create error budget and user profile tables for Phase 3.2."""

import asyncpg


async def upgrade(connection: asyncpg.Connection):
    """Create error budget and profile tables."""

    # Create user_slo_profiles table
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS user_slo_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR NOT NULL UNIQUE,
            tier VARCHAR NOT NULL,  -- 'trial', 'standard', 'premium', 'enterprise'

            -- Latency thresholds (milliseconds)
            latency_target_ms FLOAT NOT NULL,
            latency_hard_limit_ms FLOAT NOT NULL,
            latency_soft_warning_ms FLOAT NOT NULL,

            -- Confidence thresholds
            confidence_min FLOAT NOT NULL,
            confidence_escalate_threshold FLOAT NOT NULL,

            -- Query limits
            queries_per_hour INT,
            queries_per_day INT,
            max_concurrent_queries INT,

            -- Availability SLO
            availability_slo_percent FLOAT NOT NULL,
            error_rate_max_percent FLOAT NOT NULL,

            -- Features
            allow_hybrid_routing BOOLEAN DEFAULT TRUE,
            allow_sql_routing BOOLEAN DEFAULT TRUE,
            allow_rag_routing BOOLEAN DEFAULT TRUE,
            enable_caching BOOLEAN DEFAULT TRUE,
            enable_background_evaluation BOOLEAN DEFAULT FALSE,
            enable_circuit_breaker BOOLEAN DEFAULT FALSE,

            -- Enforcement
            enforce_hard_limits BOOLEAN DEFAULT TRUE,
            enforce_soft_limits BOOLEAN DEFAULT TRUE,

            -- Metadata
            is_custom BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_user_slo_profiles_user_id
            ON user_slo_profiles (user_id);
        CREATE INDEX IF NOT EXISTS idx_user_slo_profiles_tier
            ON user_slo_profiles (tier);
    """)

    # Create error_budget_windows table
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS error_budget_windows (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            month VARCHAR NOT NULL,  -- '2026-07' format
            tenant_id VARCHAR,  -- NULL for global, or tenant ID for multi-tenant

            -- Budget tracking
            total_budget_percent FLOAT NOT NULL,
            consumed_percent FLOAT DEFAULT 0.0,

            -- Metadata
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(month, tenant_id)
        );

        CREATE INDEX IF NOT EXISTS idx_error_budget_windows_month
            ON error_budget_windows (month);
        CREATE INDEX IF NOT EXISTS idx_error_budget_windows_tenant
            ON error_budget_windows (tenant_id);
    """)

    # Create error_events table
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS error_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            budget_window_id UUID NOT NULL REFERENCES error_budget_windows(id) ON DELETE CASCADE,

            -- Error details
            error_type VARCHAR NOT NULL,  -- 'latency', 'error', 'availability'
            severity VARCHAR NOT NULL,  -- 'normal', 'high', 'critical'
            description VARCHAR,
            weight FLOAT DEFAULT 1.0,  -- 1.0 for normal, 1.5 for high, 2.0 for critical

            -- Context
            query_id UUID,
            user_id VARCHAR,
            endpoint VARCHAR,
            route VARCHAR,

            -- Metadata
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_error_events_budget_window
            ON error_events (budget_window_id);
        CREATE INDEX IF NOT EXISTS idx_error_events_timestamp
            ON error_events (timestamp);
        CREATE INDEX IF NOT EXISTS idx_error_events_user_id
            ON error_events (user_id);
        CREATE INDEX IF NOT EXISTS idx_error_events_error_type
            ON error_events (error_type);
    """)

    # Create budget_snapshots table (for daily snapshots)
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS budget_snapshots (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            budget_window_id UUID NOT NULL REFERENCES error_budget_windows(id) ON DELETE CASCADE,

            -- Snapshot data
            snapshot_date DATE NOT NULL,
            consumed_percent FLOAT NOT NULL,
            burn_rate_multiplier FLOAT,
            alert_status VARCHAR,  -- 'ok', 'warning', 'critical', 'exhausted'

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_budget_snapshots_window
            ON budget_snapshots (budget_window_id);
        CREATE INDEX IF NOT EXISTS idx_budget_snapshots_date
            ON budget_snapshots (snapshot_date);
    """)

    print("✓ Created error_budget_windows, error_events, budget_snapshots, user_slo_profiles tables")


async def downgrade(connection: asyncpg.Connection):
    """Drop error budget and profile tables."""
    await connection.execute("""
        DROP TABLE IF EXISTS budget_snapshots CASCADE;
        DROP TABLE IF EXISTS error_events CASCADE;
        DROP TABLE IF EXISTS error_budget_windows CASCADE;
        DROP TABLE IF EXISTS user_slo_profiles CASCADE;
    """)

    print("✓ Dropped error budget and profile tables")
