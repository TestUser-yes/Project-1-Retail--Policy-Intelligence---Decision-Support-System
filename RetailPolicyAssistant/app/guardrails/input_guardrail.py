"""Input Guardrail - Layer 1: Validates query input."""


class InputGuardrail:
    """Validates input queries."""

    def __init__(self, max_length: int = 5000):
        self.max_length = max_length

    def check(self, query: str) -> dict:
        """Check input validity."""
        issues = []

        if not query or not query.strip():
            issues.append("Query is empty")
        elif len(query) > self.max_length:
            issues.append(f"Query exceeds max length ({self.max_length})")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
