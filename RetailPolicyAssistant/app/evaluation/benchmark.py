"""Benchmark - Baseline performance benchmarks."""

from typing import Dict, List


class Benchmark:
    """Stores and manages performance benchmarks."""

    def __init__(self):
        self.benchmarks: Dict[str, float] = {
            "latency_ms": 2000,
            "accuracy": 0.90,
            "confidence": 0.85,
        }

    def compare(self, actual: Dict[str, float]) -> dict:
        """Compare actual metrics to benchmarks."""
        comparison = {}
        
        for metric, benchmark_value in self.benchmarks.items():
            actual_value = actual.get(metric, 0)
            delta = actual_value - benchmark_value
            delta_percent = (delta / benchmark_value * 100) if benchmark_value != 0 else 0
            
            comparison[metric] = {
                "benchmark": benchmark_value,
                "actual": actual_value,
                "delta": delta,
                "delta_percent": delta_percent,
                "meets_benchmark": delta <= 0,
            }
        
        return comparison

    def update_benchmark(self, metric: str, new_value: float):
        """Update a benchmark."""
        self.benchmarks[metric] = new_value

    def get_benchmarks(self) -> Dict[str, float]:
        """Get all benchmarks."""
        return self.benchmarks
