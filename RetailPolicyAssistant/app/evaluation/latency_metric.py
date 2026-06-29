from __future__ import annotations

from app.evaluation.utils import p95


class LatencyMetric:
    def __init__(self):
        self.values = []

    def record(self, latency_seconds: float):
        self.values.append(float(latency_seconds))

    def average(self):
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

    def p95(self):
        return p95(self.values)

