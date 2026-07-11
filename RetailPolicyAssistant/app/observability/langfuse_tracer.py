"""
Langfuse integration for distributed tracing and observability.
Uses the @observe decorator for automatic, best-practice tracing.
Follows Langfuse best practices from github.com/langfuse/docs
"""

import os
from typing import Optional

from langfuse import Langfuse, observe


class LangfuseTracer:
    """
    Langfuse integration using decorators for automatic tracing.
    Best practice: use @observe decorator on functions instead of manual trace management.
    """

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseTracer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Load from settings first (which reads from .env)
        from app.core.config import settings

        self.secret_key = settings.LANGFUSE_SECRET_KEY or os.getenv("LANGFUSE_SECRET_KEY", "")
        self.public_key = settings.LANGFUSE_PUBLIC_KEY or os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.base_url = settings.LANGFUSE_BASE_URL or os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

        # Determine if Langfuse is enabled
        self.enabled = bool(self.secret_key and self.public_key)

        # Initialize Langfuse client (singleton)
        if self.enabled:
            try:
                # Initialize the Langfuse client with credentials
                # This client will be used by @observe decorator automatically
                self.client = Langfuse(
                    secret_key=self.secret_key,
                    public_key=self.public_key,
                    base_url=self.base_url,
                    flush_interval=5.0,  # Flush every 5 seconds
                    flush_at=100,  # Or when 100 spans accumulated
                )
                print("[OK] Langfuse initialized successfully")
                print(f"[OK] Tracing to: {self.base_url}")
                print("[OK] API calls will be automatically traced via @observe decorators")
            except Exception as e:
                print(f"[ERROR] Langfuse initialization failed: {e}")
                self.client = None
                self.enabled = False
        else:
            self.client = None
            print("[INFO] Langfuse tracing disabled")
            print("[INFO] Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable")

        self._initialized = True
        LangfuseTracer._client = self.client

    def get_client(self):
        """Get the Langfuse client for manual instrumentation if needed."""
        return self.client

    def is_enabled(self) -> bool:
        """Check if Langfuse tracing is enabled."""
        return self.enabled

    def log_event(self, name: str, data: dict = None):
        """Log a simple event (no-op if Langfuse disabled)."""
        # No-op - Langfuse traces are handled by @observe decorators
        pass

    def log_error(self, name: str, error_msg: str):
        """Log an error event (no-op if Langfuse disabled)."""
        # No-op - error traces handled by @observe decorators
        pass

    def flush(self):
        """Flush all pending traces to Langfuse cloud."""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                print(f"[WARNING] Langfuse flush failed: {e}")


# Global instance
_tracer = None


def get_tracer() -> LangfuseTracer:
    """Get or create global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = LangfuseTracer()
    return _tracer


def trace_function(name: Optional[str] = None, as_type: str = "span"):
    """
    Decorator to add Langfuse tracing to any function.
    Uses the Langfuse @observe decorator for best practices.

    Usage:
        @trace_function("my_operation", as_type="span")
        def my_function(query):
            return process(query)

    Args:
        name: Custom name for the traced operation (defaults to function name)
        as_type: Observation type - "span", "generation", "chain", "tool", etc.

    Returns:
        Decorated function with automatic Langfuse tracing
    """
    def decorator(func):
        operation_name = name or func.__name__
        return observe(name=operation_name, as_type=as_type)(func)
    return decorator


# Re-export observe decorator for direct use
__all__ = ["LangfuseTracer", "get_tracer", "trace_function", "observe"]
