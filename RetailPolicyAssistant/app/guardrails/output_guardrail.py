"""Output Guardrail - Layer 2: Validates response quality."""


class OutputGuardrail:
    """Validates response output."""

    def __init__(self, min_length: int = 10):
        self.min_length = min_length

    def check(self, response: str) -> dict:
        """Check output validity."""
        issues = []

        if not response or len(response) < self.min_length:
            issues.append("Response too short or empty")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
