"""Rate Limiting and Throttling

Implements token bucket algorithm for rate limiting per user and endpoint.
"""

import time
from typing import Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests_per_hour: int
    burst_size: int = None  # Allow burst up to this many requests


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.

        Args:
            capacity: Maximum tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def try_consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if consumption allowed, False if rate limit exceeded
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_tokens(self) -> float:
        """Get current token count."""
        self._refill()
        return self.tokens


class RateLimiter:
    """Rate limiter using token bucket algorithm."""

    def __init__(self):
        """Initialize rate limiter."""
        self.user_buckets: Dict[str, TokenBucket] = {}
        self.endpoint_buckets: Dict[str, TokenBucket] = {}

        # Limits
        self.user_limit = RateLimit(requests_per_hour=100)  # 100 req/hour per user
        self.endpoint_limit = RateLimit(requests_per_hour=1000)  # 1000 req/hour globally
        self.ask_limit = RateLimit(requests_per_hour=50)  # 50 /ask per hour per user

    def check_user_rate_limit(self, user_id: str) -> Tuple[bool, Dict]:
        """Check if user has rate limit remaining.

        Args:
            user_id: User ID

        Returns:
            Tuple of (allowed, info_dict)
        """
        if user_id not in self.user_buckets:
            capacity = self.user_limit.requests_per_hour
            refill_rate = capacity / 3600  # Per second
            self.user_buckets[user_id] = TokenBucket(capacity, refill_rate)

        bucket = self.user_buckets[user_id]
        allowed = bucket.try_consume(1)

        return allowed, {
            "allowed": allowed,
            "tokens_remaining": int(bucket.get_tokens()),
            "limit": self.user_limit.requests_per_hour,
        }

    def check_endpoint_rate_limit(self, endpoint: str) -> Tuple[bool, Dict]:
        """Check if endpoint has rate limit remaining.

        Args:
            endpoint: Endpoint path

        Returns:
            Tuple of (allowed, info_dict)
        """
        if endpoint not in self.endpoint_buckets:
            capacity = self.endpoint_limit.requests_per_hour
            refill_rate = capacity / 3600
            self.endpoint_buckets[endpoint] = TokenBucket(capacity, refill_rate)

        bucket = self.endpoint_buckets[endpoint]
        allowed = bucket.try_consume(1)

        return allowed, {
            "allowed": allowed,
            "tokens_remaining": int(bucket.get_tokens()),
            "limit": self.endpoint_limit.requests_per_hour,
        }

    def check_ask_limit(self, user_id: str, endpoint: str = "/ask") -> Tuple[bool, Dict]:
        """Check specific /ask endpoint rate limit.

        Args:
            user_id: User ID
            endpoint: Endpoint name

        Returns:
            Tuple of (allowed, info_dict)
        """
        key = f"{user_id}:{endpoint}"

        if key not in self.endpoint_buckets:
            capacity = self.ask_limit.requests_per_hour
            refill_rate = capacity / 3600
            self.endpoint_buckets[key] = TokenBucket(capacity, refill_rate)

        bucket = self.endpoint_buckets[key]
        allowed = bucket.try_consume(1)

        return allowed, {
            "allowed": allowed,
            "tokens_remaining": int(bucket.get_tokens()),
            "limit": self.ask_limit.requests_per_hour,
            "endpoint": endpoint,
        }

    def check_all_limits(self, user_id: str, endpoint: str) -> Tuple[bool, Dict]:
        """Check all applicable rate limits.

        Args:
            user_id: User ID
            endpoint: Endpoint path

        Returns:
            Tuple of (all_allowed, info_dict)
        """
        # Check user limit
        user_ok, user_info = self.check_user_rate_limit(user_id)

        # Check endpoint limit
        endpoint_ok, endpoint_info = self.check_endpoint_rate_limit(endpoint)

        # Check specific /ask limit if applicable
        ask_ok, ask_info = (True, {})
        if endpoint == "/ask":
            ask_ok, ask_info = self.check_ask_limit(user_id, endpoint)

        all_allowed = user_ok and endpoint_ok and ask_ok

        return all_allowed, {
            "allowed": all_allowed,
            "user_limit": user_info,
            "endpoint_limit": endpoint_info,
            "ask_limit": ask_info if endpoint == "/ask" else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_stats(self) -> Dict:
        """Get rate limiter statistics."""
        return {
            "active_users": len(self.user_buckets),
            "active_endpoints": len(self.endpoint_buckets),
            "user_limit_per_hour": self.user_limit.requests_per_hour,
            "endpoint_limit_per_hour": self.endpoint_limit.requests_per_hour,
            "ask_limit_per_hour": self.ask_limit.requests_per_hour,
        }

    def reset_user_limit(self, user_id: str) -> None:
        """Reset rate limit for a user."""
        if user_id in self.user_buckets:
            del self.user_buckets[user_id]

    def reset_endpoint_limit(self, endpoint: str) -> None:
        """Reset rate limit for an endpoint."""
        if endpoint in self.endpoint_buckets:
            del self.endpoint_buckets[endpoint]

    def reset_all_limits(self) -> None:
        """Reset all rate limits."""
        self.user_buckets.clear()
        self.endpoint_buckets.clear()


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Helper functions

def check_rate_limit(user_id: str, endpoint: str) -> Tuple[bool, Dict]:
    """Check rate limits for user and endpoint.

    Args:
        user_id: User ID
        endpoint: Endpoint path

    Returns:
        Tuple of (allowed, info)
    """
    limiter = get_rate_limiter()
    return limiter.check_all_limits(user_id, endpoint)


def get_rate_limit_info(user_id: str, endpoint: str) -> Dict:
    """Get rate limit info for user and endpoint.

    Args:
        user_id: User ID
        endpoint: Endpoint path

    Returns:
        Rate limit info dict
    """
    allowed, info = check_rate_limit(user_id, endpoint)
    return info
