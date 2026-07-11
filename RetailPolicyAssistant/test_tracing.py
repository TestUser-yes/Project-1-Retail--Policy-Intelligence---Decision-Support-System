#!/usr/bin/env python3
"""Test script to verify Langfuse tracing is working."""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_langfuse_status():
    """Check Langfuse status endpoint."""
    print("\n=== Testing Langfuse Status ===")
    try:
        url = f"{BASE_URL}/api/observability/langfuse-status"
        print(f"Requesting: {url}")
        resp = requests.get(url)
        data = resp.json()
        print(f"Status: {json.dumps(data, indent=2)}")

        if data.get("langfuse_enabled"):
            print("OK - Langfuse is ENABLED")
            return True
        else:
            print("FAIL - Langfuse is DISABLED")
            return False
    except Exception as e:
        print(f"FAIL - Error checking status: {e}")
        return False


def test_query_with_tracing():
    """Test query endpoint with tracing."""
    print("\n=== Testing Query with Tracing ===")

    # Get token
    try:
        token_resp = requests.get(f"{BASE_URL}/token")
        token = token_resp.json()["access_token"]
        print(f"OK - Got token: {token[:20]}...")
    except Exception as e:
        print(f"FAIL - Failed to get token: {e}")
        return

    # Make query
    try:
        headers = {"Authorization": f"Bearer {token}"}
        query_data = {"query": "What is the data retention policy?"}

        print(f"Sending query: {query_data['query']}")
        resp = requests.post(
            f"{BASE_URL}/api/ask",
            json=query_data,
            headers=headers,
            timeout=30
        )

        if resp.status_code == 200:
            data = resp.json()
            print(f"OK - Query succeeded")
            print(f"  Route: {data.get('route')}")
            print(f"  Confidence: {data.get('confidence_score')}")
            print(f"  Latency: {data.get('latency_seconds'):.2f}s")
            print(f"  Agents used: {data.get('agents_used')}")

            # Small delay to let Langfuse flush
            print("\nWaiting 2s for Langfuse to flush traces...")
            time.sleep(2)

        else:
            print(f"FAIL - Query failed: {resp.status_code}")
            print(f"  Response: {resp.text}")

    except Exception as e:
        print(f"FAIL - Error making query: {e}")


if __name__ == "__main__":
    print("Testing Langfuse Observability Tracing")
    print("=" * 50)

    # Test status
    enabled = test_langfuse_status()

    if enabled:
        # Test actual query tracing
        test_query_with_tracing()
        print("\nOK - Tracing test complete")
        print("Check your Langfuse dashboard at: https://cloud.langfuse.com")
        print("You should see new traces from 'ask_query', 'rag_pipeline', or 'sql_query'")
    else:
        print("\nFAIL - Langfuse not enabled, skipping query test")
