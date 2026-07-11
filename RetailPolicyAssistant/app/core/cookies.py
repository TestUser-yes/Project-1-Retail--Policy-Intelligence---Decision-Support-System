"""Secure cookie-based token management."""

from fastapi import Response
from datetime import datetime, timedelta
from app.config import get_config


class SecureCookieManager:
    """Manages secure httpOnly cookies for authentication tokens."""

    def __init__(self):
        config = get_config()
        self.domain = getattr(config, 'cookie_domain', 'localhost')
        self.secure = getattr(config, 'cookie_secure', False)  # Set to True in production with HTTPS
        self.samesite = getattr(config, 'cookie_samesite', 'lax')
        self.access_token_max_age = 30 * 60  # 30 minutes
        self.refresh_token_max_age = 7 * 24 * 60 * 60  # 7 days

    def set_access_token_cookie(self, response: Response, token: str):
        """Set secure httpOnly cookie for access token."""
        response.set_cookie(
            key="access_token",
            value=token,
            max_age=self.access_token_max_age,
            expires=datetime.utcnow() + timedelta(seconds=self.access_token_max_age),
            httponly=True,  # Not accessible from JavaScript (XSS protection)
            secure=self.secure,  # Only sent over HTTPS in production
            samesite=self.samesite,  # CSRF protection
            domain=self.domain,
            path="/",
        )

    def set_refresh_token_cookie(self, response: Response, token: str):
        """Set secure httpOnly cookie for refresh token."""
        response.set_cookie(
            key="refresh_token",
            value=token,
            max_age=self.refresh_token_max_age,
            expires=datetime.utcnow() + timedelta(seconds=self.refresh_token_max_age),
            httponly=True,
            secure=self.secure,
            samesite=self.samesite,
            domain=self.domain,
            path="/",
        )

    def clear_auth_cookies(self, response: Response):
        """Clear authentication cookies (logout)."""
        response.delete_cookie(
            key="access_token",
            domain=self.domain,
            path="/",
            secure=self.secure,
            httponly=True,
            samesite=self.samesite,
        )
        response.delete_cookie(
            key="refresh_token",
            domain=self.domain,
            path="/",
            secure=self.secure,
            httponly=True,
            samesite=self.samesite,
        )

    def set_csrf_token_cookie(self, response: Response, token: str):
        """Set CSRF protection token in cookie (accessible from JavaScript for sending in headers)."""
        response.set_cookie(
            key="csrf_token",
            value=token,
            max_age=24 * 60 * 60,  # 24 hours
            httponly=False,  # Accessible from JavaScript to include in headers
            secure=self.secure,
            samesite=self.samesite,
            domain=self.domain,
            path="/",
        )


def get_cookie_manager() -> SecureCookieManager:
    """Get singleton cookie manager instance."""
    return SecureCookieManager()
