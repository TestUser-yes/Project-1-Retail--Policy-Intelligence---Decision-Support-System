"""Repository for SLO metrics storage and queries."""

import asyncpg
from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any


class SLOMetricsRepository:
    """Manages SLO metrics storage and queries."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize repository with database pool.

        Args:
            db_pool: asyncpg connection pool
        """
        self.db_pool = db_pool

    async def insert_metric(
        self,
        endpoint: str,
        route: str,
        latency_ms: float,
        confidence_score: float,
        query_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
        p50_ms: Optional[float] = None,
        p95_ms: Optional[float] = None,
        p99_ms: Optional[float] = None,
        slo_breached: bool = False,
        breach_type: Optional[str] = None,
        breach_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Insert a new SLO metric.

        Args:
            endpoint: API endpoint (e.g., '/ask')
            route: Query route ('rag', 'sql', 'hybrid')
            latency_ms: Request latency in milliseconds
            confidence_score: Answer confidence (0.0-1.0)
            query_id: Optional query ID
            user_id: Optional user ID
            p50_ms: p50 percentile latency
            p95_ms: p95 percentile latency
            p99_ms: p99 percentile latency
            slo_breached: Whether SLO was breached
            breach_type: Type of breach ('latency', 'confidence')
            breach_reason: Reason for breach

        Returns:
            Inserted metric with ID and timestamp
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO slo_metrics (
                    endpoint, route, latency_ms, confidence_score,
                    query_id, user_id, p50_latency_ms, p95_latency_ms, p99_latency_ms,
                    slo_breached, breach_type, breach_reason
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id, timestamp;
            """, endpoint, route, latency_ms, confidence_score,
                query_id, user_id, p50_ms, p95_ms, p99_ms,
                slo_breached, breach_type, breach_reason)

            return dict(result) if result else {}

    async def get_percentiles(
        self,
        route: Optional[str] = None,
        minutes: int = 60,
    ) -> Dict[str, float]:
        """Get latency percentiles for recent metrics.

        Args:
            route: Optional route filter
            minutes: Time window in minutes

        Returns:
            Dictionary with p50, p95, p99 percentiles
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        query = "SELECT latency_ms FROM slo_metrics WHERE timestamp > $1"
        params = [cutoff]

        if route:
            query += " AND route = $2"
            params.append(route)

        query += " ORDER BY latency_ms"

        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        if not rows:
            return {"p50": 0, "p95": 0, "p99": 0, "count": 0}

        latencies = [row['latency_ms'] for row in rows]
        n = len(latencies)

        def percentile(p):
            idx = int((p / 100.0) * (n - 1))
            idx = max(0, min(idx, n - 1))
            return latencies[idx]

        return {
            "p50": round(percentile(50), 2),
            "p95": round(percentile(95), 2),
            "p99": round(percentile(99), 2),
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
            "mean": round(sum(latencies) / n, 2),
            "count": n,
        }

    async def get_slo_compliance(
        self,
        route: Optional[str] = None,
        minutes: int = 60,
        target_ms: float = 2000.0,
    ) -> Dict[str, Any]:
        """Get SLO compliance percentage.

        Args:
            route: Optional route filter
            minutes: Time window in minutes
            target_ms: SLO target in milliseconds

        Returns:
            Compliance statistics
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN latency_ms <= $2 THEN 1 ELSE 0 END) as compliant
            FROM slo_metrics
            WHERE timestamp > $1
        """
        params = [cutoff, target_ms]

        if route:
            query += " AND route = $3"
            params.append(route)

        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow(query, *params)

        total = result['total'] or 0
        compliant = result['compliant'] or 0

        return {
            "total": total,
            "compliant": compliant,
            "compliance_pct": round((compliant / total * 100), 2) if total > 0 else 0,
            "target_ms": target_ms,
            "window_minutes": minutes,
        }

    async def get_breaches(
        self,
        limit: int = 100,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Get recent SLO breaches.

        Args:
            limit: Maximum number of breaches to return
            hours: Time window in hours

        Returns:
            List of recent breach records
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    id, timestamp, endpoint, route, latency_ms, confidence_score,
                    breach_type, breach_reason
                FROM slo_metrics
                WHERE slo_breached = TRUE AND timestamp > $1
                ORDER BY timestamp DESC
                LIMIT $2;
            """, cutoff, limit)

        return [dict(row) for row in rows]

    async def get_metrics_by_route(
        self,
        minutes: int = 60,
    ) -> Dict[str, Dict[str, Any]]:
        """Get aggregated metrics by route.

        Args:
            minutes: Time window in minutes

        Returns:
            Metrics broken down by route
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    route,
                    COUNT(*) as count,
                    AVG(latency_ms) as avg_latency,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99,
                    SUM(CASE WHEN slo_breached THEN 1 ELSE 0 END)::float / COUNT(*) as breach_rate
                FROM slo_metrics
                WHERE timestamp > $1
                GROUP BY route;
            """, cutoff)

        result = {}
        for row in rows:
            route = row['route']
            result[route] = {
                "count": row['count'],
                "avg_latency_ms": round(row['avg_latency'], 2),
                "p50_latency_ms": round(row['p50'] or 0, 2),
                "p95_latency_ms": round(row['p95'] or 0, 2),
                "p99_latency_ms": round(row['p99'] or 0, 2),
                "breach_rate": round(row['breach_rate'] or 0, 4),
            }

        return result

    async def get_summary(
        self,
        minutes: int = 60,
    ) -> Dict[str, Any]:
        """Get summary of SLO metrics.

        Args:
            minutes: Time window in minutes

        Returns:
            Summary statistics
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_queries,
                    AVG(latency_ms) as avg_latency,
                    AVG(confidence_score) as avg_confidence,
                    SUM(CASE WHEN slo_breached THEN 1 ELSE 0 END) as breach_count,
                    SUM(CASE WHEN slo_breached THEN 1 ELSE 0 END)::float / COUNT(*) as breach_rate
                FROM slo_metrics
                WHERE timestamp > $1;
            """, cutoff)

        return {
            "total_queries": result['total_queries'] or 0,
            "avg_latency_ms": round(result['avg_latency'] or 0, 2),
            "avg_confidence": round(result['avg_confidence'] or 0, 2),
            "breach_count": result['breach_count'] or 0,
            "breach_rate_pct": round((result['breach_rate'] or 0) * 100, 2),
            "window_minutes": minutes,
        }


# Global instance
_slo_metrics_repo: Optional[SLOMetricsRepository] = None


def get_slo_metrics_repo(db_pool: asyncpg.Pool) -> SLOMetricsRepository:
    """Get or create SLO metrics repository instance."""
    global _slo_metrics_repo
    if _slo_metrics_repo is None or _slo_metrics_repo.db_pool != db_pool:
        _slo_metrics_repo = SLOMetricsRepository(db_pool)
    return _slo_metrics_repo
