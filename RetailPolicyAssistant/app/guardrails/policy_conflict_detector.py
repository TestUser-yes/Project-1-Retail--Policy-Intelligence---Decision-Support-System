"""Policy Conflict Detector - Layer 5: Detects policy conflicts."""


class PolicyConflictDetector:
    """Detects conflicting policies."""

    CONFLICTING_TERMS = [
        ("delete", "preserve"),
        ("approved", "rejected"),
        ("urgent", "delayed"),
    ]

    def check(self, text: str) -> dict:
        """Check for policy conflicts."""
        text_lower = text.lower()
        conflicts = []

        for term1, term2 in self.CONFLICTING_TERMS:
            if term1 in text_lower and term2 in text_lower:
                conflicts.append(f"Conflicting terms: {term1} and {term2}")

        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
        }
