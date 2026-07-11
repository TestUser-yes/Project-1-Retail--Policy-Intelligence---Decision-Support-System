#!/usr/bin/env python
"""Test Langfuse connection and trace sending."""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.observability.langfuse_tracer import get_tracer, trace_function
import time


print("=" * 60)
print("LANGFUSE CONNECTION TEST")
print("=" * 60)

# 1. Check environment variables
print("\n[1] Checking environment variables...")
print(f"    LANGFUSE_PUBLIC_KEY: {'SET' if settings.LANGFUSE_PUBLIC_KEY else 'NOT SET'}")
print(f"    LANGFUSE_SECRET_KEY: {'SET' if settings.LANGFUSE_SECRET_KEY else 'NOT SET'}")
print(f"    LANGFUSE_BASE_URL: {settings.LANGFUSE_BASE_URL}")

# 2. Initialize tracer
print("\n[2] Initializing Langfuse tracer...")
tracer = get_tracer()
print(f"    Tracer enabled: {tracer.is_enabled()}")
print(f"    Tracer client: {'ACTIVE' if tracer.client else 'INACTIVE'}")

if not tracer.is_enabled():
    print("\n❌ LANGFUSE IS DISABLED - Check your credentials!")
    sys.exit(1)

# 3. Send test trace
print("\n[3] Sending test trace...")

@trace_function("test_trace", as_type="span")
def test_function():
    """Test function that sends a trace."""
    time.sleep(0.1)
    return {"status": "success", "message": "Test trace sent"}

result = test_function()
print(f"    Test result: {result}")

# 4. Flush traces
print("\n[4] Flushing traces to Langfuse cloud...")
try:
    tracer.flush()
    print("    [OK] Traces flushed (may take a few seconds to appear in UI)")
except Exception as e:
    print(f"    [ERROR] Flush failed: {e}")
    if "401" in str(e):
        print("    >>> CREDENTIALS INVALID - Your API keys are rejected by Langfuse!")
        print("    >>> ACTION: Regenerate API keys from https://cloud.langfuse.com/settings/api-keys")

# 5. Check client info
print("\n[5] Client details:")
if tracer.client:
    print(f"    Base URL: {tracer.client.base_url if hasattr(tracer.client, 'base_url') else 'N/A'}")
    print(f"    Batch size: {tracer.client.flush_at if hasattr(tracer.client, 'flush_at') else 'N/A'}")
    print(f"    Flush interval: {tracer.client.flush_interval if hasattr(tracer.client, 'flush_interval') else 'N/A'}s")

print("\n" + "=" * 60)
print("✅ TEST COMPLETE - Check Langfuse dashboard for trace")
print("=" * 60)
print("\nNext steps:")
print("1. Open https://cloud.langfuse.com/dashboard")
print("2. Go to project 'RetailProject'")
print("3. Check the 'Tracing' tab")
print("4. You should see a trace named 'test_trace'")
print("\nIf no trace appears:")
print("- Verify credentials are correct")
print("- Wait 5-10 seconds for trace to appear")
print("- Check browser console for errors")
