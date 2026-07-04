"""Evaluation metrics - Measures system performance."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class EvaluationMetrics:
    """Metrics for evaluating system performance."""
    
    # Latency metrics
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    
    # Accuracy metrics
    task_success_rate: float
    route_accuracy: float
    answer_accuracy: float
    risk_classification_accuracy: float
    
    # Escalation metrics
    escalation_rate: float
    false_escalation_rate: float
    missed_escalation_rate: float
    
    # Confidence metrics
    avg_confidence: float
    confidence_correlation: float  # Correlation with accuracy
    
    # Cost metrics
    avg_cost_per_query: float
    total_cost: float


class MetricsCalculator:
    """Calculates evaluation metrics."""

    def calculate_latency_metrics(self, latencies: List[float]) -> dict:
        """Calculate latency metrics."""
        if not latencies:
            return {"avg": 0, "p95": 0, "p99": 0}
        
        sorted_latencies = sorted(latencies)
        avg = sum(latencies) / len(latencies)
        p95_idx = int(len(latencies) * 0.95)
        p99_idx = int(len(latencies) * 0.99)
        
        return {
            "avg": avg,
            "p95": sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else 0,
            "p99": sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0,
        }

    def calculate_accuracy_metrics(self, results: List[dict]) -> dict:
        """Calculate accuracy metrics."""
        if not results:
            return {"task_success_rate": 0, "avg_accuracy": 0}
        
        successful = sum(1 for r in results if r.get("success"))
        task_success_rate = successful / len(results)
        
        return {"task_success_rate": task_success_rate}

    def calculate_escalation_metrics(self, escalations: List[dict]) -> dict:
        """Calculate escalation metrics."""
        if not escalations:
            return {"escalation_rate": 0}
        
        total = len(escalations)
        necessary = sum(1 for e in escalations if e.get("necessary"))
        
        return {
            "escalation_rate": total,
            "accuracy": necessary / total if total > 0 else 0,
        }
