"""Migration: Create SLO metrics table for Phase 3.1."""

import asyncpg


async def upgrade(connection: asyncpg.Connection):
    """Create slo_metrics table."""
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS slo_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            endpoint VARCHAR NOT NULL,
            route VARCHAR NOT NULL,
            query_id UUID,
            user_id VARCHAR,

            -- Latency metrics
            latency_ms FLOAT NOT NULL,
            p50_latency_ms FLOAT,
            p95_latency_ms FLOAT,
            p99_latency_ms FLOAT,

            -- Quality metrics
            confidence_score FLOAT,
            answer_relevance FLOAT,

            -- SLO compliance
            slo_breached BOOLEAN DEFAULT FALSE,
            breach_type VARCHAR,
            breach_reason VARCHAR,

            -- Context
            retrieval_latency_ms FLOAT,
            llm_latency_ms FLOAT,
            doc_count INT DEFAULT 0,

            -- Routing
            route_confidence FLOAT,
            sql_correctness FLOAT
        );

        -- Create indexes for fast queries
        CREATE INDEX IF NOT EXISTS idx_slo_metrics_timestamp
            ON slo_metrics (timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_slo_metrics_route
            ON slo_metrics (route);
        CREATE INDEX IF NOT EXISTS idx_slo_metrics_user_id
            ON slo_metrics (user_id);
        CREATE INDEX IF NOT EXISTS idx_slo_metrics_breached
            ON slo_metrics (slo_breached);

        -- Composite indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_slo_metrics_route_timestamp
            ON slo_metrics (route, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_slo_metrics_user_timestamp
            ON slo_metrics (user_id, timestamp DESC);
    """)

    print("✓ Created slo_metrics table")


async def downgrade(connection: asyncpg.Connection):
    """Drop slo_metrics table."""
    await connection.execute("""
        DROP TABLE IF EXISTS slo_metrics CASCADE;
    """)

    print("✓ Dropped slo_metrics table")


# If using Alembic-style migrations, uncomment below:
# from alembic import op
# import sqlalchemy as sa
#
# def upgrade():
#     op.create_table('slo_metrics',
#         sa.Column('id', sa.UUID(), nullable=False, server_default=sa.func.gen_random_uuid()),
#         sa.Column('timestamp', sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp()),
#         ...
#     )
#
# def downgrade():
#     op.drop_table('slo_metrics')
