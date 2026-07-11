"""CSRF protection middleware and utilities."""

import secrets
import hashlib
from typing import Dict

# In-memory CSRF token store (in production, use Redis)
_csrf_tokens: Dict[str, Dict] = {}


def generate_csrf_token() -> str:
    """Generate a CSRF protection token."""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    _csrf_tokens[token_hash] = {"created": __import__("datetime").datetime.utcnow()}
    return token


def verify_csrf_token(token: str) -> bool:
    """Verify CSRF token validity."""
    if not token:
        return False

    token_hash = hashlib.sha256(token.encode()).hexdigest()

    if token_hash not in _csrf_tokens:
        return False

    # Token is valid, remove it (single-use)
    _csrf_tokens.pop(token_hash, None)
    return True


def create_csrf_exempt_methods():
    """Return HTTP methods exempt from CSRF protection."""
    return {"GET", "HEAD", "OPTIONS", "TRACE"}
