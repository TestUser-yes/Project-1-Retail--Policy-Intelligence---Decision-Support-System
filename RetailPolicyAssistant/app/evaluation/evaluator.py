"""Evaluator - Evaluates system performance against benchmarks."""

from app.evaluation.metrics import EvaluationMetrics


class SystemEvaluator:
    """Evaluates system against capstone requirements."""

    # SLO targets from capstone spec
    SLO_TARGETS = {
        "task_success_rate": 0.90,  # 90%
        "p95_latency_ms": 3000,  # 3 seconds
        "route_accuracy": 0.95,  # 95%
        "risk_accuracy": 0.95,  # 95%
        "escalation_accuracy": 1.00,  # 100%
    }

    def evaluate(self, metrics: EvaluationMetrics) -> dict:
        """Evaluate metrics against SLO targets."""
        results = {
            "task_success_rate": {
                "actual": metrics.task_success_rate,
                "target": self.SLO_TARGETS["task_success_rate"],
                "pass": metrics.task_success_rate >= self.SLO_TARGETS["task_success_rate"],
            },
            "p95_latency": {
                "actual": metrics.p95_latency_ms,
                "target": self.SLO_TARGETS["p95_latency_ms"],
                "pass": metrics.p95_latency_ms <= self.SLO_TARGETS["p95_latency_ms"],
            },
            "route_accuracy": {
                "actual": metrics.route_accuracy,
                "target": self.SLO_TARGETS["route_accuracy"],
                "pass": metrics.route_accuracy >= self.SLO_TARGETS["route_accuracy"],
            },
        }
        
        all_pass = all(r["pass"] for r in results.values())
        
        return {
            "overall_pass": all_pass,
            "results": results,
            "compliance_rate": sum(1 for r in results.values() if r["pass"]) / len(results),
        }
