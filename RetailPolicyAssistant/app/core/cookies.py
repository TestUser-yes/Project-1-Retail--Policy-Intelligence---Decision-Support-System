"""Secure cookie-based token management."""

from fastapi import Response
from datetime import datetime, timedelta, timezone
from app.config import get_config


class SecureCookieManager:
    """Manages secure httpOnly cookies for authentication tokens."""

    def __init__(self):
        config = get_config()
        # For development: don't set domain so cookies work across localhost/127.0.0.1
        # For production: set domain explicitly via environment variable
        self.domain = getattr(config, 'cookie_domain', None)
        self.secure = getattr(config, 'cookie_secure', False)  # Set to True in production with HTTPS
        self.samesite = getattr(config, 'cookie_samesite', 'lax')
        self.access_token_max_age = 30 * 60  # 30 minutes
        self.refresh_token_max_age = 7 * 24 * 60 * 60  # 7 days

    def set_access_token_cookie(self, response: Response, token: str):
        """Set secure httpOnly cookie for access token."""
        cookie_kwargs = {
            "key": "access_token",
            "value": token,
            "max_age": self.access_token_max_age,
            "expires": datetime.now(timezone.utc) + timedelta(seconds=self.access_token_max_age),
            "httponly": True,
            "secure": self.secure,
            "samesite": self.samesite,
            "path": "/",
        }
        if self.domain:
            cookie_kwargs["domain"] = self.domain
        response.set_cookie(**cookie_kwargs)

    def set_refresh_token_cookie(self, response: Response, token: str):
        """Set secure httpOnly cookie for refresh token."""
        cookie_kwargs = {
            "key": "refresh_token",
            "value": token,
            "max_age": self.refresh_token_max_age,
            "expires": datetime.now(timezone.utc) + timedelta(seconds=self.refresh_token_max_age),
            "httponly": True,
            "secure": self.secure,
            "samesite": self.samesite,
            "path": "/",
        }
        if self.domain:
            cookie_kwargs["domain"] = self.domain
        response.set_cookie(**cookie_kwargs)

    def clear_auth_cookies(self, response: Response):
        """Clear authentication cookies (logout)."""
        cookie_kwargs_access = {
            "key": "access_token",
            "path": "/",
            "secure": self.secure,
            "httponly": True,
            "samesite": self.samesite,
        }
        if self.domain:
            cookie_kwargs_access["domain"] = self.domain
        response.delete_cookie(**cookie_kwargs_access)

        cookie_kwargs_refresh = {
            "key": "refresh_token",
            "path": "/",
            "secure": self.secure,
            "httponly": True,
            "samesite": self.samesite,
        }
        if self.domain:
            cookie_kwargs_refresh["domain"] = self.domain
        response.delete_cookie(**cookie_kwargs_refresh)

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
