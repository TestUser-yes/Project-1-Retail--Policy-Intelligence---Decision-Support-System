from __future__ import annotations

from app.evaluation.utils import coerce_bool


class EscalationMetric:
    def __init__(self):
        self.correct = 0
        self.total = 0
        self.high_risk_correct = 0
        self.high_risk_total = 0

    def evaluate(self, expected: bool, predicted, risk_level: str | None = None):
        self.total += 1
        expected_value = coerce_bool(expected)
        predicted_value = coerce_bool(predicted)
        passed = expected_value == predicted_value
        if passed:
            self.correct += 1

        if (risk_level or "").strip().lower() == "high":
            self.high_risk_total += 1
            if predicted_value is True:
                self.high_risk_correct += 1

        return {
            "passed": passed,
            "reason": "" if passed else f"Expected escalate '{expected_value}', got '{predicted_value}'",
        }

    def score(self):
        if self.total == 0:
            return 0.0
        return self.correct / self.total

    def high_risk_score(self):
        if self.high_risk_total == 0:
            return 1.0
        return self.high_risk_correct / self.high_risk_total

