"""PII Detector - Layer 3: Detects personally identifiable information."""

import re


class PIIDetector:
    """Detects PII in queries and responses."""

    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'

    def check(self, text: str) -> dict:
        """Check for PII in text."""
        pii_found = {
            "emails": re.findall(self.EMAIL_PATTERN, text),
            "phone_numbers": re.findall(self.PHONE_PATTERN, text),
            "ssns": re.findall(self.SSN_PATTERN, text),
        }

        has_pii = any(pii_found.values())

        return {
            "has_pii": has_pii,
            "pii_types": pii_found,
        }

    def mask_pii(self, text: str) -> str:
        """Mask PII in text."""
        text = re.sub(self.EMAIL_PATTERN, "[EMAIL]", text)
        text = re.sub(self.PHONE_PATTERN, "[PHONE]", text)
        text = re.sub(self.SSN_PATTERN, "[SSN]", text)
        return text
