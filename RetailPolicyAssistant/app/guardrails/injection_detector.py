"""Injection Detector - Layer 4: Detects injection attacks."""

import re


class InjectionDetector:
    """Detects injection attack attempts."""

    SQL_INJECTION_PATTERNS = [
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\b)",
        r"(;.*?(SELECT|INSERT|UPDATE|DELETE))",
        r"(OR\s+1\s*=\s*1)",
    ]

    def check(self, text: str) -> dict:
        """Check for injection attempts."""
        injections = []

        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                injections.append(f"Potential injection: {pattern}")

        return {
            "has_injection": len(injections) > 0,
            "injections": injections,
        }
