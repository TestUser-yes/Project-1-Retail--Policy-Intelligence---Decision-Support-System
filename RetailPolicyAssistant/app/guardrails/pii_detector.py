"""PII Detector - Layer 3: Detects personally identifiable information and secrets.

Extended detection includes:
- Personal identifiers: email, phone, SSN, credit card
- API Keys and tokens: OpenAI, Anthropic, AWS, bearer tokens
- JWT tokens
- Database URLs and connection strings
- Passwords and credentials
- Private cryptographic keys
"""

import re
from typing import Dict, List, Tuple


class PIIDetector:
    """Detects PII and secrets in queries and responses."""

    # Personal information patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'

    # API Key and token patterns
    OPENAI_API_KEY_PATTERN = r'sk-[a-zA-Z0-9]{20,}'
    ANTHROPIC_API_KEY_PATTERN = r'sk-ant-[a-zA-Z0-9]{20,}'
    HUGGINGFACE_API_KEY_PATTERN = r'hf_[a-zA-Z0-9]{20,}'
    AWS_ACCESS_KEY_PATTERN = r'AKIA[0-9A-Z]{16}'
    AWS_SECRET_KEY_PATTERN = r'(?i)aws_secret_access_key\s*=\s*[a-zA-Z0-9/+]{40}'
    AZURE_KEY_PATTERN = r'[a-zA-Z0-9_-]{32,}'  # Generic 32+ char key (broad pattern)
    GENERIC_API_KEY_PATTERN = r'(?:api[_-]?key|apikey|api-key)[\s]*[=:]\s*["\']?([a-zA-Z0-9_\-]{10,})["\']?'

    # JWT token pattern
    JWT_TOKEN_PATTERN = r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'

    # Bearer token pattern
    BEARER_TOKEN_PATTERN = r'Bearer\s+([a-zA-Z0-9_\-\.]+)'

    # Database and connection string patterns
    DATABASE_URL_PATTERN = r'(postgresql|postgres|mongodb|mysql|redis|mariadb)://[^\s]+'
    DATABASE_CONNECTION_PATTERN = r'(Server|Data Source|Host|Database|User|Password|Uid|Pwd)[\s]*=[\s]*[^\s;,]+'
    SQLSERVER_CONNECTION_PATTERN = r'(Server|Data\s+Source|Initial\s+Catalog|User\s+ID|Password)[\s]*=[\s]*[^\s;]+'

    # Password and secret patterns
    PASSWORD_LITERAL_PATTERN = r'(?:password|passwd|pwd|secret)[\s]*[=:]\s*["\']?([a-zA-Z0-9!@#$%^&*()_+=\[\]{};:"\\|,.<>?]{6,})["\']?'
    PRIVATE_KEY_PATTERN = r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----'
    GITHUB_TOKEN_PATTERN = r'gh[pou]_[a-zA-Z0-9_]{36,255}'

    def check(self, text: str) -> Dict:
        """Check for PII and secrets in text.

        Args:
            text: Text to scan for PII/secrets

        Returns:
            {
                "has_pii": bool,
                "pii_types": dict,
                "secrets_found": list,
            }
        """
        pii_found = {
            "emails": re.findall(self.EMAIL_PATTERN, text),
            "phone_numbers": re.findall(self.PHONE_PATTERN, text),
            "ssns": re.findall(self.SSN_PATTERN, text),
            "credit_cards": re.findall(self.CREDIT_CARD_PATTERN, text),
        }

        secrets_found = []

        # Check for API keys
        if re.search(self.OPENAI_API_KEY_PATTERN, text):
            secrets_found.append("OpenAI API key")
        if re.search(self.ANTHROPIC_API_KEY_PATTERN, text):
            secrets_found.append("Anthropic API key")
        if re.search(self.HUGGINGFACE_API_KEY_PATTERN, text):
            secrets_found.append("HuggingFace API key")
        if re.search(self.AWS_ACCESS_KEY_PATTERN, text):
            secrets_found.append("AWS access key")
        if re.search(self.AWS_SECRET_KEY_PATTERN, text, re.IGNORECASE):
            secrets_found.append("AWS secret key")
        if re.search(self.GENERIC_API_KEY_PATTERN, text, re.IGNORECASE):
            secrets_found.append("Generic API key")

        # Check for JWT tokens
        if re.search(self.JWT_TOKEN_PATTERN, text):
            secrets_found.append("JWT token")

        # Check for bearer tokens
        if re.search(self.BEARER_TOKEN_PATTERN, text):
            secrets_found.append("Bearer token")

        # Check for database URLs and connection strings
        if re.search(self.DATABASE_URL_PATTERN, text):
            secrets_found.append("Database URL")
        if re.search(self.DATABASE_CONNECTION_PATTERN, text):
            secrets_found.append("Database connection string")
        if re.search(self.SQLSERVER_CONNECTION_PATTERN, text, re.IGNORECASE):
            secrets_found.append("SQL Server connection string")

        # Check for passwords and secrets
        if re.search(self.PASSWORD_LITERAL_PATTERN, text, re.IGNORECASE):
            secrets_found.append("Password literal")
        if re.search(self.PRIVATE_KEY_PATTERN, text):
            secrets_found.append("Private cryptographic key")
        if re.search(self.GITHUB_TOKEN_PATTERN, text):
            secrets_found.append("GitHub token")

        has_pii = any(pii_found.values()) or len(secrets_found) > 0

        return {
            "has_pii": has_pii,
            "pii_types": pii_found,
            "secrets_found": secrets_found,
        }

    def mask_pii(self, text: str) -> str:
        """Mask PII and secrets in text.

        Args:
            text: Text to sanitize

        Returns:
            Text with PII/secrets redacted
        """
        # Mask personal information
        text = re.sub(self.EMAIL_PATTERN, "[EMAIL]", text)
        text = re.sub(self.PHONE_PATTERN, "[PHONE]", text)
        text = re.sub(self.SSN_PATTERN, "[SSN]", text)
        text = re.sub(self.CREDIT_CARD_PATTERN, "[CREDIT_CARD]", text)

        # Mask API keys (order matters - more specific patterns first)
        text = re.sub(self.OPENAI_API_KEY_PATTERN, "[OPENAI_API_KEY]", text)
        text = re.sub(self.ANTHROPIC_API_KEY_PATTERN, "[ANTHROPIC_API_KEY]", text)
        text = re.sub(self.HUGGINGFACE_API_KEY_PATTERN, "[HUGGINGFACE_API_KEY]", text)
        text = re.sub(self.AWS_ACCESS_KEY_PATTERN, "[AWS_ACCESS_KEY]", text)
        text = re.sub(self.AWS_SECRET_KEY_PATTERN, "[AWS_SECRET_KEY]", text, flags=re.IGNORECASE)
        text = re.sub(self.GENERIC_API_KEY_PATTERN, "[API_KEY]", text, flags=re.IGNORECASE)

        # Mask tokens
        text = re.sub(self.JWT_TOKEN_PATTERN, "[JWT_TOKEN]", text)
        text = re.sub(self.BEARER_TOKEN_PATTERN, "Bearer [TOKEN]", text)
        text = re.sub(self.GITHUB_TOKEN_PATTERN, "[GITHUB_TOKEN]", text)

        # Mask database and connection information
        text = re.sub(self.DATABASE_URL_PATTERN, "[DATABASE_URL]", text)
        text = re.sub(self.DATABASE_CONNECTION_PATTERN, "[DATABASE_CONNECTION]", text)
        text = re.sub(self.SQLSERVER_CONNECTION_PATTERN, "[CONNECTION_STRING]", text, flags=re.IGNORECASE)

        # Mask passwords and keys
        text = re.sub(self.PASSWORD_LITERAL_PATTERN, "[PASSWORD]", text, flags=re.IGNORECASE)
        text = re.sub(self.PRIVATE_KEY_PATTERN, "[PRIVATE_KEY]", text)

        return text

    def extract_pii_summary(self, text: str) -> str:
        """Extract PII summary for logging (redacted).

        Args:
            text: Text to analyze

        Returns:
            Redacted summary string for logging
        """
        check = self.check(text)

        summary_parts = []

        if check["pii_types"]["emails"]:
            summary_parts.append(f"emails:{len(check['pii_types']['emails'])}")
        if check["pii_types"]["phone_numbers"]:
            summary_parts.append(f"phones:{len(check['pii_types']['phone_numbers'])}")
        if check["pii_types"]["ssns"]:
            summary_parts.append(f"ssns:{len(check['pii_types']['ssns'])}")
        if check["pii_types"]["credit_cards"]:
            summary_parts.append(f"cards:{len(check['pii_types']['credit_cards'])}")

        for secret in check["secrets_found"]:
            summary_parts.append(secret)

        return " | ".join(summary_parts) if summary_parts else "None"
