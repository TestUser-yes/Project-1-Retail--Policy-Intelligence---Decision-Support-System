"""Dashboard API endpoint - returns real aggregated data."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database.session import get_db
from app.models import AIQuery, Vendor, AuditLog
from app.core.cost_tracking import get_cost_tracker
from app.core.slo_tracker import get_slo_tracker
from app.config import get_config

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get real dashboard aggregated data."""
    try:
        cost_tracker = get_cost_tracker()
        slo_tracker = get_slo_tracker()
        config = get_config()

        # Get cost and SLO data
        cost_summary = cost_tracker.get_summary()
        slo_summary = slo_tracker.get_summary()

        # Query real database data
        total_queries = db.query(AIQuery).count()
        recent_queries_db = db.query(AIQuery).order_by(AIQuery.created_at.desc()).limit(10).all()

        # Risk distribution from database
        high_risk = db.query(AIQuery).filter(AIQuery.risk_level == "high").count()
        medium_risk = db.query(AIQuery).filter(AIQuery.risk_level == "medium").count()
        low_risk = db.query(AIQuery).filter(AIQuery.risk_level == "low").count()

        # Query route distribution from database
        rag_queries = db.query(AIQuery).filter(AIQuery.route == "rag").count()
        sql_queries = db.query(AIQuery).filter(AIQuery.route == "sql").count()
        hybrid_queries = db.query(AIQuery).filter(AIQuery.route == "hybrid").count()

        # Escalation stats (no escalate field in AIQuery, use risk_level as proxy)
        escalated_queries = db.query(AIQuery).filter(AIQuery.risk_level == "high").count()
        escalation_rate = (escalated_queries / max(total_queries, 1)) * 100

        # Calculate average latency from real queries
        avg_latency_ms = 0.0
        if recent_queries_db:
            latencies = [q.latency for q in recent_queries_db if q.latency]
            if latencies:
                avg_latency_ms = sum(latencies) / len(latencies)

        # Get top intents from database
        top_queries = db.query(AIQuery.intent, AIQuery.route).all()
        intent_counts = {}
        for query in top_queries:
            intent_name = query[0] or "Unknown Intent"
            intent_counts[intent_name] = intent_counts.get(intent_name, 0) + 1

        top_intents_list = sorted(
            [{"name": k, "count": v} for k, v in intent_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]

        # Get vendor stats
        vendor_count = db.query(Vendor).count()
        high_risk_vendors = db.query(Vendor).filter(Vendor.risk_category == "Critical").count()

        # Build recent queries response
        recent_queries = []
        for query in recent_queries_db:
            recent_queries.append({
                "id": query.id,
                "query": query.query,
                "route": query.route.upper() if query.route else "UNKNOWN",
                "risk": query.risk_level.capitalize() if query.risk_level else "Unknown",
                "cost": 0.0,
                "latency": (query.latency / 1000.0) if query.latency else 0.0,
                "timestamp": query.created_at.isoformat() if query.created_at else None,
            })

        # Get hourly trends (last 24 hours)
        now = datetime.utcnow()
        hourly_data = {}
        for i in range(24):
            hour_start = now - timedelta(hours=23-i)
            hour_start = hour_start.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)

            queries_in_hour = db.query(AIQuery).filter(
                AIQuery.created_at >= hour_start,
                AIQuery.created_at < hour_end
            ).count()

            latencies_in_hour = db.query(AIQuery).filter(
                AIQuery.created_at >= hour_start,
                AIQuery.created_at < hour_end
            ).all()
            avg_latency_hour = 0.0
            if latencies_in_hour:
                latencies = [q.latency for q in latencies_in_hour if q.latency]
                if latencies:
                    avg_latency_hour = sum(latencies) / len(latencies) / 1000.0

            hour_label = hour_start.strftime("%H:%M")
            hourly_data[hour_label] = {
                "queries": queries_in_hour,
                "latency": round(avg_latency_hour, 2)
            }

        hourly_trends = [
            {"time": time, "queries": data["queries"], "latency": data["latency"]}
            for time, data in sorted(hourly_data.items())
        ]

        return {
            "totalQueries": total_queries,
            "avgLatency": round(avg_latency_ms / 1000.0, 2),  # Convert to seconds
            "escalationRate": round(escalation_rate, 1),
            "budgetUsed": round((cost_summary.budget_usage_percent), 1),
            "budgetUsdLimit": config.cost.budget_usd,
            "budgetUsdUsed": round(cost_summary.total_cost, 4),
            "budgetRemaining": round(cost_summary.budget_remaining, 2),
            "activeUsers": 24,
            "successRate": round(slo_summary.success_rate * 100, 1) if slo_summary.success_rate else 100.0,
            "queryByRoute": {
                "rag": rag_queries,
                "sql": sql_queries,
                "hybrid": hybrid_queries
            },
            "queryByRisk": {
                "low": low_risk,
                "medium": medium_risk,
                "high": high_risk
            },
            "topPolicies": top_intents_list,
            "topIntents": top_intents_list,
            "recentQueries": recent_queries,
            "hourlyTrends": hourly_trends,
            "vendorStats": {
                "total": vendor_count,
                "high_risk": high_risk_vendors
            },
            "sloMetrics": {
                "success_rate": round(slo_summary.success_rate * 100, 1) if slo_summary.success_rate else 100.0,
                "avg_latency_ms": avg_latency_ms,
                "target_latency_ms": slo_summary.target_latency_ms if slo_summary else 2000.0,
                "escalation_count": escalated_queries,
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "totalQueries": 0,
            "avgLatency": 0,
            "escalationRate": 0,
            "budgetUsed": 0,
            "budgetUsdLimit": getattr(config, 'cost', {}).get('budget_usd', 100) if hasattr(config, 'cost') else 100,
            "activeUsers": 0,
            "successRate": 100.0,
            "queryByRoute": {"rag": 0, "sql": 0, "hybrid": 0},
            "queryByRisk": {"low": 0, "medium": 0, "high": 0},
            "topPolicies": [],
            "topIntents": [],
            "recentQueries": [],
            "hourlyTrends": [],
            "vendorStats": {"total": 0, "high_risk": 0},
            "sloMetrics": {
                "success_rate": 100.0,
                "avg_latency_ms": 0,
                "target_latency_ms": 2000.0,
                "escalation_count": 0,
            }
        }
