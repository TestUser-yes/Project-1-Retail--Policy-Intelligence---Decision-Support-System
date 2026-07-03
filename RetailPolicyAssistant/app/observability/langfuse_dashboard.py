"""
Langfuse observability dashboard and reporting utilities.
Provides insights into system performance, costs, and trace data.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json


class LangfuseDashboard:
    """
    Dashboard utilities for analyzing Langfuse trace data.
    Provides metrics, reports, and insights.
    """

    def __init__(self, tracer=None):
        self.tracer = tracer
        self._metrics = {
            "total_queries": 0,
            "total_cost": 0.0,
            "total_latency": 0.0,
            "error_count": 0,
            "success_count": 0,
            "by_route": {},
            "by_intent": {},
            "by_risk_level": {},
            "by_user": {},
        }

    def record_query_metrics(
        self,
        query: str,
        intent: str,
        route: str,
        risk_level: str,
        cost_usd: float,
        latency_seconds: float,
        user_id: str,
        success: bool = True,
    ):
        """Record metrics from a query execution."""
        self._metrics["total_queries"] += 1
        self._metrics["total_cost"] += cost_usd
        self._metrics["total_latency"] += latency_seconds

        if success:
            self._metrics["success_count"] += 1
        else:
            self._metrics["error_count"] += 1

        # By route
        if route not in self._metrics["by_route"]:
            self._metrics["by_route"][route] = {
                "count": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
            }
        self._metrics["by_route"][route]["count"] += 1
        self._metrics["by_route"][route]["total_cost"] += cost_usd
        self._metrics["by_route"][route]["avg_latency"] = (
            self._metrics["by_route"][route].get("avg_latency", 0) * 0.9 +
            latency_seconds * 0.1
        )

        # By intent
        if intent not in self._metrics["by_intent"]:
            self._metrics["by_intent"][intent] = {"count": 0}
        self._metrics["by_intent"][intent]["count"] += 1

        # By risk level
        if risk_level not in self._metrics["by_risk_level"]:
            self._metrics["by_risk_level"][risk_level] = {"count": 0}
        self._metrics["by_risk_level"][risk_level]["count"] += 1

        # By user
        if user_id not in self._metrics["by_user"]:
            self._metrics["by_user"][user_id] = {
                "count": 0,
                "total_cost": 0.0,
                "queries": [],
            }
        self._metrics["by_user"][user_id]["count"] += 1
        self._metrics["by_user"][user_id]["total_cost"] += cost_usd

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get high-level metrics summary."""
        total_queries = self._metrics["total_queries"]

        return {
            "total_queries": total_queries,
            "total_cost_usd": round(self._metrics["total_cost"], 4),
            "average_latency_ms": round(
                (self._metrics["total_latency"] / total_queries * 1000)
                if total_queries > 0 else 0,
                2
            ),
            "success_rate": round(
                (self._metrics["success_count"] / total_queries * 100)
                if total_queries > 0 else 0,
                2
            ),
            "error_count": self._metrics["error_count"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_route_distribution(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics broken down by routing decision."""
        result = {}
        for route, metrics in self._metrics["by_route"].items():
            result[route] = {
                "queries": metrics["count"],
                "total_cost_usd": round(metrics["total_cost"], 4),
                "avg_latency_ms": round(metrics["avg_latency"] * 1000, 2),
            }
        return result

    def get_intent_distribution(self) -> Dict[str, int]:
        """Get count of queries by detected intent."""
        return {
            intent: metrics["count"]
            for intent, metrics in self._metrics["by_intent"].items()
        }

    def get_risk_distribution(self) -> Dict[str, int]:
        """Get count of queries by risk level."""
        return {
            risk_level: metrics["count"]
            for risk_level, metrics in self._metrics["by_risk_level"].items()
        }

    def get_user_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get per-user metrics."""
        result = {}
        for user_id, metrics in self._metrics["by_user"].items():
            result[user_id] = {
                "queries": metrics["count"],
                "total_cost_usd": round(metrics["total_cost"], 4),
            }
        return result

    def get_top_users_by_cost(self, limit: int = 10) -> List[tuple]:
        """Get top users by total cost."""
        users = [
            (user_id, metrics["total_cost"])
            for user_id, metrics in self._metrics["by_user"].items()
        ]
        return sorted(users, key=lambda x: x[1], reverse=True)[:limit]

    def get_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive observability report."""
        return {
            "report_timestamp": datetime.utcnow().isoformat(),
            "summary": self.get_summary_metrics(),
            "by_route": self.get_route_distribution(),
            "by_intent": self.get_intent_distribution(),
            "by_risk_level": self.get_risk_distribution(),
            "by_user": self.get_user_metrics(),
            "top_users_by_cost": [
                {"user_id": user_id, "cost_usd": round(cost, 4)}
                for user_id, cost in self.get_top_users_by_cost()
            ],
        }

    def print_report(self):
        """Print formatted report to console."""
        report = self.get_full_report()

        print("\n" + "=" * 80)
        print("LANGFUSE OBSERVABILITY REPORT")
        print("=" * 80)
        print(f"\nReport Generated: {report['report_timestamp']}")

        print("\n--- SUMMARY METRICS ---")
        summary = report["summary"]
        print(f"Total Queries: {summary['total_queries']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Total Cost: ${summary['total_cost_usd']}")
        print(f"Average Latency: {summary['average_latency_ms']}ms")
        print(f"Errors: {summary['error_count']}")

        print("\n--- ROUTING DISTRIBUTION ---")
        for route, metrics in report["by_route"].items():
            print(f"  {route}: {metrics['queries']} queries, "
                  f"${metrics['total_cost_usd']}, "
                  f"{metrics['avg_latency_ms']}ms")

        print("\n--- INTENT DISTRIBUTION ---")
        for intent, count in report["by_intent"].items():
            print(f"  {intent}: {count} queries")

        print("\n--- RISK DISTRIBUTION ---")
        for risk_level, count in report["by_risk_level"].items():
            print(f"  {risk_level}: {count} queries")

        print("\n--- TOP USERS BY COST ---")
        for user in report["top_users_by_cost"][:5]:
            print(f"  {user['user_id']}: ${user['cost_usd']}")

        print("\n" + "=" * 80 + "\n")

    def export_json(self, filepath: str):
        """Export report as JSON."""
        report = self.get_full_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report exported to {filepath}")


# Global dashboard instance
_dashboard = None


def get_dashboard(tracer=None) -> LangfuseDashboard:
    """Get or create global dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = LangfuseDashboard(tracer=tracer)
    return _dashboard
