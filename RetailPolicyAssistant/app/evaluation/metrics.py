"""
Legacy compatibility metric.

The new evaluation flow uses dedicated metric classes in:
route_metric.py, answer_metric.py, risk_metric.py,
escalation_metric.py, and latency_metric.py.
"""

class TSRMetric:
    def __init__(self):
        self.correct = 0
        self.total = 0

    def update(self, predicted: str, expected: str):
        self.total += 1
        if predicted == expected:
            self.correct += 1

    def score(self):
        if self.total == 0:
            return 0.0
        return self.correct / self.total
