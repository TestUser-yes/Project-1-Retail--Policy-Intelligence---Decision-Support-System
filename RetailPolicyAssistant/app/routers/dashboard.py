"""Dashboard API endpoint - returns aggregated data from database."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.session import get_db
from app.models import AIQuery
from app.models.evaluation import Phase2Run, Phase2Result
from app.core.auth import get_current_user, User
from app.evaluation.tsr import get_tsr_calculator
from app.evaluation.config import get_evaluation_config
from app.evaluation.retrieval_metrics import get_retrieval_metrics_calculator

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get dashboard aggregated data from Neon PostgreSQL."""
    try:
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

        # Escalation stats
        escalated_queries = db.query(AIQuery).filter(AIQuery.risk_level == "high").count()
        escalation_rate = (escalated_queries / max(total_queries, 1)) * 100

        # Calculate average latency from real queries
        avg_latency_ms = 0.0
        if recent_queries_db:
            latencies = [q.latency for q in recent_queries_db if q.latency]
            if latencies:
                avg_latency_ms = sum(latencies) / len(latencies)

        # Get top intents from database
        top_queries = db.query(AIQuery.intent).all()
        intent_counts = {}
        for query in top_queries:
            intent_name = query[0] or "Unknown Intent"
            intent_counts[intent_name] = intent_counts.get(intent_name, 0) + 1

        top_intents_list = sorted(
            [{"name": k, "count": v} for k, v in intent_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]

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

        # Get hourly trends (last 24 hours) - simplified for performance
        hourly_trends = []
        try:
            now = datetime.utcnow()
            for i in range(24):
                hour_start = now - timedelta(hours=23-i)
                hour_start = hour_start.replace(minute=0, second=0, microsecond=0)
                hour_end = hour_start + timedelta(hours=1)

                queries_in_hour = db.query(AIQuery).filter(
                    AIQuery.created_at >= hour_start,
                    AIQuery.created_at < hour_end
                ).count()

                hour_label = hour_start.strftime("%H:%M")
                hourly_trends.append({
                    "time": hour_label,
                    "queries": queries_in_hour,
                    "latency": avg_latency_ms / 1000.0 if queries_in_hour > 0 else 0.0
                })
        except Exception as e:
            # If hourly trends fail, just use empty list
            print(f"[WARNING] Hourly trends query failed: {e}")
            hourly_trends = []

        # ===== PHASE 2: RETRIEVAL QUALITY METRICS =====
        # Query Phase 2 aggregates from database
        retrieval_metrics = {
            "contextPrecision": {
                "current": 0.0,
                "trend": "stable",
                "status": "good",
                "lastUpdated": None
            },
            "contextRecall": {
                "current": 0.0,
                "trend": "stable",
                "status": "good",
                "lastUpdated": None
            }
        }

        try:
            # Get latest Phase 2 run
            latest_phase2_run = db.query(Phase2Run).order_by(Phase2Run.run_time.desc()).first()
            if latest_phase2_run:
                retrieval_metrics["contextPrecision"]["current"] = round(latest_phase2_run.avg_context_precision, 4)
                retrieval_metrics["contextRecall"]["current"] = round(latest_phase2_run.avg_context_recall, 4)
                retrieval_metrics["contextPrecision"]["lastUpdated"] = latest_phase2_run.run_time.isoformat()
                retrieval_metrics["contextRecall"]["lastUpdated"] = latest_phase2_run.run_time.isoformat()

                # Determine status based on thresholds
                from app.evaluation.config import get_metric_status
                retrieval_metrics["contextPrecision"]["status"] = get_metric_status(
                    "context_precision",
                    latest_phase2_run.avg_context_precision
                )
                retrieval_metrics["contextRecall"]["status"] = get_metric_status(
                    "context_recall",
                    latest_phase2_run.avg_context_recall
                )
        except Exception as e:
            print(f"[WARNING] Phase 2 metrics query failed: {e}")

        return {
            "totalQueries": total_queries,
            "avgLatency": round(avg_latency_ms / 1000.0, 2),
            "escalationRate": round(escalation_rate, 1),
            "budgetUsed": 0.0,
            "budgetUsdLimit": 100.0,
            "budgetUsdUsed": 0.0,
            "budgetRemaining": 100.0,
            "activeUsers": 5,
            "successRate": 95.0,
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
                "total": 10,
                "high_risk": 2
            },
            "sloMetrics": {
                "success_rate": 95.0,
                "avg_latency_ms": avg_latency_ms,
                "target_latency_ms": 2000.0,
                "escalation_count": escalated_queries,
            },
            "retrievalMetrics": retrieval_metrics
        }
    except Exception as e:
        import traceback
        error_msg = f"Dashboard error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get("/metrics/phase1")
async def get_phase1_metrics(
    current_user: User = Depends(get_current_user),
):
    """Get Phase 1 evaluation metrics for AI Operational Dashboard.

    Returns aggregated metrics for Latency, Task Success Rate (TSR),
    and SQL Correctness. This endpoint is independent of main dashboard
    and does not modify existing behavior.

    Phase 1 Metrics:
    - Latency: Request processing time and breakdown by stage
    - TSR: Task Success Rate - ratio of successful to failed queries
    - SQL Correctness: SQL validation and injection detection results
    """
    try:
        config = get_evaluation_config()
        tsr_calc = get_tsr_calculator()

        # Get TSR summary
        tsr_summary = tsr_calc.get_summary()
        tsr_current = tsr_summary.get("rolling_window", {}).get("tsr", 0.0)

        return {
            "phase": 1,
            "timestamp": datetime.utcnow().isoformat(),
            "enabled": {
                "latency": config.enable_latency,
                "tsr": config.enable_tsr,
                "sql_correctness": config.enable_sql_correctness,
            },
            "metrics": {
                "latency": {
                    "description": "Request processing latency",
                    "unit": "ms",
                    "status": "good",
                    "note": "Tracked per-query in orchestrator background evaluation",
                    "data_available": False,  # Per-query basis
                },
                "tsr": {
                    "description": "Task Success Rate",
                    "current": round(tsr_current, 4),
                    "current_percent": round(tsr_current * 100, 2),
                    "status": tsr_summary.get("status", "good"),
                    "successful": tsr_summary.get("rolling_window", {}).get("successful", 0),
                    "total": tsr_summary.get("rolling_window", {}).get("total", 0),
                    "unit": "ratio",
                    "data_available": tsr_summary.get("rolling_window", {}).get("total", 0) > 0,
                },
                "sql_correctness": {
                    "description": "SQL query validation and correctness",
                    "unit": "confidence_score",
                    "status": "good",
                    "note": "Tracked per-SQL-query in orchestrator background evaluation",
                    "data_available": False,  # Per-query basis
                },
            },
            "configuration": {
                "background_enabled": config.enable_background_evaluation,
                "timeout_seconds": config.evaluation_timeout_seconds,
                "max_concurrent": config.max_concurrent_evaluations,
            },
            "note": "Phase 1 evaluation runs asynchronously in background. Metrics accumulate over time.",
        }
    except Exception as e:
        import traceback
        error_msg = f"Phase 1 metrics error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return {
            "phase": 1,
            "error": error_msg,
            "status": "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/metrics/phase2")
async def get_phase2_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Phase 2 retrieval quality metrics for AI Operational Dashboard.

    Returns aggregated metrics for Context Precision and Context Recall.
    These metrics measure the quality of document retrieval in the RAG pipeline.

    Phase 2 Metrics:
    - Context Precision: Relevance of retrieved documents to the query
    - Context Recall: Completeness of retrieval - did we get all relevant info?
    """
    try:
        config = get_evaluation_config()
        calc = get_retrieval_metrics_calculator()

        # Get rolling window stats
        rolling_stats = calc.get_rolling_stats()
        global_stats = calc.get_global_stats()

        # Get precision and recall from rolling window
        precision_current = rolling_stats.get("precision", {}).get("avg", 0.0)
        recall_current = rolling_stats.get("recall", {}).get("avg", 0.0)

        # Determine status
        from app.evaluation.config import get_metric_status
        precision_status = get_metric_status("context_precision", precision_current)
        recall_status = get_metric_status("context_recall", recall_current)

        # Try to get latest run from database for more detail
        latest_run = db.query(Phase2Run).order_by(Phase2Run.run_time.desc()).first()
        last_updated = latest_run.run_time.isoformat() if latest_run else None

        return {
            "phase": 2,
            "timestamp": datetime.utcnow().isoformat(),
            "enabled": {
                "context_precision": config.enable_context_precision,
                "context_recall": config.enable_context_recall,
            },
            "metrics": {
                "context_precision": {
                    "description": "Relevance of retrieved documents",
                    "current": round(precision_current, 4),
                    "current_percent": round(precision_current * 100, 2),
                    "status": precision_status,
                    "min": round(rolling_stats.get("precision", {}).get("min", 0.0), 4),
                    "max": round(rolling_stats.get("precision", {}).get("max", 0.0), 4),
                    "median": round(rolling_stats.get("precision", {}).get("median", 0.0), 4),
                    "unit": "ratio",
                    "data_available": rolling_stats.get("count", 0) > 0,
                },
                "context_recall": {
                    "description": "Completeness of document retrieval",
                    "current": round(recall_current, 4),
                    "current_percent": round(recall_current * 100, 2),
                    "status": recall_status,
                    "min": round(rolling_stats.get("recall", {}).get("min", 0.0), 4),
                    "max": round(rolling_stats.get("recall", {}).get("max", 0.0), 4),
                    "median": round(rolling_stats.get("recall", {}).get("median", 0.0), 4),
                    "unit": "ratio",
                    "data_available": rolling_stats.get("count", 0) > 0,
                },
            },
            "statistics": {
                "total_evaluations": global_stats.get("total_evals", 0),
                "rolling_window_count": rolling_stats.get("count", 0),
                "global_avg_precision": round(global_stats.get("avg_precision", 0.0), 4),
                "global_avg_recall": round(global_stats.get("avg_recall", 0.0), 4),
                "last_updated": last_updated,
            },
            "configuration": {
                "background_enabled": config.enable_background_evaluation,
                "timeout_seconds": config.evaluation_timeout_seconds,
            },
            "note": "Phase 2 evaluation runs asynchronously for RAG/Hybrid queries. Metrics accumulate over time.",
        }
    except Exception as e:
        import traceback
        error_msg = f"Phase 2 metrics error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return {
            "phase": 2,
            "error": error_msg,
            "status": "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
        }
