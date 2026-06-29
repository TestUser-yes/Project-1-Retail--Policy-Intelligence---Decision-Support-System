from __future__ import annotations

from app.evaluation.utils import normalize_text


class RouteMetric:
    def __init__(self):
        self.correct = 0
        self.total = 0

    def evaluate(self, expected: str, predicted: str):
        self.total += 1
        expected_value = normalize_text(expected).strip().lower()
        predicted_value = normalize_text(predicted).strip().lower()
        passed = expected_value == predicted_value
        if passed:
            self.correct += 1
        return {
            "passed": passed,
            "reason": "" if passed else f"Expected route '{expected_value}', got '{predicted_value}'",
        }

    def score(self):
        if self.total == 0:
            return 0.0
        return self.correct / self.total

