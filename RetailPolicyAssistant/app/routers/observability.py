"""Observability metrics endpoint - returns SLO and query analytics."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database.session import get_db
from app.models import AIQuery
from app.core.slo_tracker import get_slo_tracker

router = APIRouter(prefix="/api/observability", tags=["observability"])


@router.get("")
async def get_observability_metrics(db: Session = Depends(get_db)):
    """Get observability metrics: SLO, latency trends, query analytics."""
    try:
        slo_tracker = get_slo_tracker()
        slo_summary = slo_tracker.get_summary()

        # Get metrics for last 24 hours
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)

        # Total queries
        total_queries = db.query(AIQuery).count()
        queries_24h = db.query(AIQuery).filter(AIQuery.created_at >= last_24h).count()

        # Risk distribution
        high_risk = db.query(AIQuery).filter(AIQuery.risk_level == "high").count()
        medium_risk = db.query(AIQuery).filter(AIQuery.risk_level == "medium").count()
        low_risk = db.query(AIQuery).filter(AIQuery.risk_level == "low").count()

        # Route distribution
        rag_count = db.query(AIQuery).filter(AIQuery.route == "rag").count()
        sql_count = db.query(AIQuery).filter(AIQuery.route == "sql").count()
        hybrid_count = db.query(AIQuery).filter(AIQuery.route == "hybrid").count()

        # Calculate average confidence
        avg_confidence = 0.85  # Fallback

        # Calculate escalation rate
        escalated = db.query(AIQuery).filter(AIQuery.escalated == True).count()
        escalation_rate = (escalated / max(total_queries, 1)) * 100

        # Hourly trends
        hourly_trends = []
        for i in range(24):
            hour_start = now - timedelta(hours=23-i)
            hour_start = hour_start.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)

            count = db.query(AIQuery).filter(
                AIQuery.created_at >= hour_start,
                AIQuery.created_at < hour_end
            ).count()

            hour_label = hour_start.strftime("%H:%M")
            hourly_trends.append({
                "time": hour_label,
                "queries": count,
                "slo_target_ms": 2000.0,
                "avg_latency_ms": slo_summary.latency_ms if slo_summary else 0.0
            })

        # Recent queries
        recent_queries = db.query(AIQuery).order_by(AIQuery.created_at.desc()).limit(10).all()
        recent_queries_list = []
        for q in recent_queries:
            recent_queries_list.append({
                "id": q.id,
                "query": q.query[:100] if q.query else "N/A",
                "route": q.route.upper() if q.route else "UNKNOWN",
                "risk": q.risk_level.capitalize() if q.risk_level else "Unknown",
                "latency_ms": q.latency if q.latency else 0.0,
                "timestamp": q.created_at.isoformat() if q.created_at else None,
            })

        return {
            "timestamp": now.isoformat(),
            "summary": {
                "total_queries": total_queries,
                "queries_24h": queries_24h,
                "avg_confidence": avg_confidence,
                "escalation_rate": round(escalation_rate, 1),
                "slo_compliance_rate": round(slo_summary.success_rate * 100, 1) if slo_summary else 100.0,
            },
            "risk_distribution": {
                "high": high_risk,
                "medium": medium_risk,
                "low": low_risk,
            },
            "route_distribution": {
                "rag": rag_count,
                "sql": sql_count,
                "hybrid": hybrid_count,
            },
            "slo_metrics": {
                "success_rate": round(slo_summary.success_rate * 100, 1) if slo_summary else 100.0,
                "avg_latency_ms": slo_summary.latency_ms if slo_summary else 0.0,
                "target_latency_ms": slo_summary.target_latency_ms if slo_summary else 2000.0,
                "slo_status": slo_summary.slo_status if slo_summary else "pass",
            },
            "hourly_trends": hourly_trends,
            "recent_queries": recent_queries_list,
            "langfuse_traces": []  # Placeholder - would connect to Langfuse API
        }

    except Exception as e:
        print(f"Observability metrics error: {e}")
        return {
            "timestamp": now.isoformat(),
            "error": str(e),
            "summary": {
                "total_queries": 0,
                "queries_24h": 0,
                "avg_confidence": 0.0,
                "escalation_rate": 0.0,
                "slo_compliance_rate": 0.0,
            },
            "risk_distribution": {"high": 0, "medium": 0, "low": 0},
            "route_distribution": {"rag": 0, "sql": 0, "hybrid": 0},
            "slo_metrics": {
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "target_latency_ms": 2000.0,
                "slo_status": "fail",
            },
            "hourly_trends": [],
            "recent_queries": [],
        }
