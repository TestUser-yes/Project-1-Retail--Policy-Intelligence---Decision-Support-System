"""
Cost Tracking & Budget Management

Tracks Ollama embedding costs and API usage (if switching to paid LLM).
Currently: Ollama is FREE (local), no costs tracked.
For future: Claude/OpenAI integration ready.
"""

import time
import uuid
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class QueryCost:
    """Track cost for a single query."""
    query_id: str
    timestamp: datetime
    query_text: str
    embedding_tokens: int = 0
    completion_tokens: int = 0
    embedding_cost: float = 0.0
    completion_cost: float = 0.0
    total_cost: float = 0.0
    model: str = "ollama"  # Local embeddings (free)

    def __post_init__(self):
        self.total_cost = self.embedding_cost + self.completion_cost


@dataclass
class BudgetLimits:
    """Define budget constraints per capstone requirements (README.md)."""
    # Constants from app/config/constants.py BUDGET_CONFIG
    daily_limit: float = 100.0  # $100/day (for paid LLM)
    monthly_limit: float = 2000.0  # $2000/month
    per_query_limit: float = 1.0  # $1 max per query
    alert_threshold: float = 0.80  # Alert at 80% usage


@dataclass
class CostSummary:
    """Cost statistics."""
    total_queries: int = 0
    total_cost: float = 0.0
    avg_cost_per_query: float = 0.0
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    budget_usage_percent: float = 0.0
    queries_this_hour: int = 0
    queries_today: int = 0
    queries_this_month: int = 0
    budget_remaining: float = 0.0  # Will be set after calculation


class CostTracker:
    """Track and manage query costs."""

    def __init__(self, budget: BudgetLimits = None):
        self.budget = budget or BudgetLimits()
        self.queries: List[QueryCost] = []
        self.start_time = time.time()

    def record_query(
        self,
        query_text: str,
        query_id: str = None,
        embedding_tokens: int = 0,
        completion_tokens: int = 0,
        embedding_cost: float = 0.0,
        completion_cost: float = 0.0,
    ):
        """Record a query execution and its cost."""
        if query_id is None:
            query_id = str(uuid.uuid4())

        query_cost = QueryCost(
            query_id=query_id,
            timestamp=datetime.now(timezone.utc),
            query_text=query_text,
            embedding_tokens=embedding_tokens,
            completion_tokens=completion_tokens,
            embedding_cost=embedding_cost,
            completion_cost=completion_cost,
        )
        self.queries.append(query_cost)
        return query_cost

    def get_summary(self) -> CostSummary:
        """Get cost statistics."""
        now = datetime.now(timezone.utc)

        # Filter queries by time period
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        today_queries = [q for q in self.queries if q.timestamp >= today_start]
        hour_queries = [q for q in self.queries if q.timestamp >= hour_start]
        month_queries = [q for q in self.queries if q.timestamp >= month_start]

        total_cost = sum(q.total_cost for q in self.queries)
        daily_cost = sum(q.total_cost for q in today_queries)
        monthly_cost = sum(q.total_cost for q in month_queries)

        avg_cost = (
            total_cost / len(self.queries)
            if self.queries
            else 0.0
        )

        budget_usage = (daily_cost / self.budget.daily_limit) * 100
        budget_remaining = self.budget.daily_limit - daily_cost

        return CostSummary(
            total_queries=len(self.queries),
            total_cost=total_cost,
            avg_cost_per_query=avg_cost,
            daily_cost=daily_cost,
            monthly_cost=monthly_cost,
            budget_usage_percent=budget_usage,
            queries_this_hour=len(hour_queries),
            queries_today=len(today_queries),
            queries_this_month=len(month_queries),
            budget_remaining=budget_remaining,
        )

    def check_budget(self) -> Dict:
        """Check if within budget limits."""
        summary = self.get_summary()

        checks = {
            "daily_limit_ok": summary.daily_cost <= self.budget.daily_limit,
            "monthly_limit_ok": summary.monthly_cost <= self.budget.monthly_limit,
            "alert_threshold": summary.budget_usage_percent >= (self.budget.alert_threshold * 100),
            "summary": summary,
        }

        return checks

    def estimate_cost(self, embedding_tokens: int = 0, completion_tokens: int = 0) -> float:
        """
        Estimate cost for a query.

        For Ollama (local): 0.0
        For Claude API: Would calculate based on token counts
        For OpenAI: Would calculate based on model pricing
        """
        # Current: Ollama is FREE
        # If switching to Claude API:
        # - Embedding: ~$0.00002 per 1K tokens
        # - Completion: ~$0.003 per 1K completion tokens

        return 0.0  # Free (local Ollama)

    def log_cost_warning(self, message: str):
        """Log cost-related warnings."""
        import logging
        logger = logging.getLogger("cost")
        logger.warning(f"Cost Alert: {message}")

    def get_cost_report(self) -> str:
        """Generate cost report."""
        summary = self.get_summary()
        checks = self.check_budget()

        daily_limit_status = "OK" if checks['daily_limit_ok'] else "EXCEEDED"
        monthly_limit_status = "OK" if checks['monthly_limit_ok'] else "EXCEEDED"
        alert_status = "YES" if checks['alert_threshold'] else "NO"

        report = f"""
========================================
        COST TRACKING REPORT
=====================================

USAGE STATISTICS:
  Total Queries: {summary.total_queries}
  Total Cost: ${summary.total_cost:.2f}
  Avg Cost/Query: ${summary.avg_cost_per_query:.4f}

TIME-BASED METRICS:
  Queries This Hour: {summary.queries_this_hour}
  Queries Today: {summary.queries_today}
  Queries This Month: {summary.queries_this_month}

COST BY PERIOD:
  Daily Cost: ${summary.daily_cost:.2f} / ${self.budget.daily_limit:.2f}
  Monthly Cost: ${summary.monthly_cost:.2f} / ${self.budget.monthly_limit:.2f}

BUDGET STATUS:
  Daily Usage: {summary.budget_usage_percent:.1f}%
  Daily Limit: {daily_limit_status}
  Monthly Limit: {monthly_limit_status}
  Alert Triggered: {alert_status}

CURRENT MODEL: Ollama (Local/Free)
Future Support: Ready for Claude API or OpenAI integration
"""
        return report


# Global instance
_cost_tracker = None


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


def record_query_cost(
    query_text: str,
    query_id: str = None,
    embedding_tokens: int = 0,
    completion_tokens: int = 0,
):
    """Record query cost globally."""
    tracker = get_cost_tracker()

    # Estimate costs (currently 0 for Ollama)
    embedding_cost = tracker.estimate_cost(embedding_tokens, 0)
    completion_cost = tracker.estimate_cost(0, completion_tokens)

    return tracker.record_query(
        query_text=query_text,
        query_id=query_id,
        embedding_tokens=embedding_tokens,
        completion_tokens=completion_tokens,
        embedding_cost=embedding_cost,
        completion_cost=completion_cost,
    )


def print_cost_report():
    """Print cost report."""
    tracker = get_cost_tracker()
    print(tracker.get_cost_report())
