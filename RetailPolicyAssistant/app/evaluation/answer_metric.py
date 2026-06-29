from __future__ import annotations

from app.evaluation.utils import contains_keywords, normalize_text


class AnswerMetric:
    def __init__(self):
        self.correct = 0
        self.total = 0

    def evaluate(self, expected, predicted):
        self.total += 1

        if isinstance(expected, dict):
            keywords = expected.get("answer_contains", [])
        else:
            keywords = expected or []

        if isinstance(keywords, str):
            keywords = [keywords]

        text = normalize_text(predicted)
        passed, missing = contains_keywords(text, list(keywords))
        if passed:
            self.correct += 1

        return {
            "passed": passed,
            "reason": "" if passed else f"Missing answer keywords: {', '.join(missing)}",
        }

    def score(self):
        if self.total == 0:
            return 0.0
        return self.correct / self.total

