#!/usr/bin/env python
"""Test API endpoint and verify Langfuse tracing is working."""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

print("=" * 70)
print("LANGFUSE TRACING END-TO-END TEST")
print("=" * 70)

# Step 1: Health check
print("\n[1] Health check...")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"    Status: {resp.status_code}")
    print(f"    Response: {resp.json()}")
except Exception as e:
    print(f"    ERROR: {e}")
    print("    -> Make sure API is running: python -m uvicorn app.main:app --reload --port 8000")
    sys.exit(1)

# Step 2: Get token
print("\n[2] Getting demo token...")
try:
    resp = requests.get(f"{BASE_URL}/token", timeout=5)
    token_data = resp.json()
    access_token = token_data["access_token"]
    print(f"    Token obtained: {access_token[:50]}...")
except Exception as e:
    print(f"    ERROR: {e}")
    sys.exit(1)

# Step 3: Make query that triggers traces
print("\n[3] Making query to trigger traces...")
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

queries = [
    "What is our return policy?",
    "How do I process a refund?",
    "What are the warranty terms?"
]

for query in queries:
    print(f"\n    Query: '{query}'")
    try:
        resp = requests.post(
            f"{BASE_URL}/ask",
            headers=headers,
            json={
                "query": query,
                "conversation_id": ""
            },
            timeout=30
        )

        if resp.status_code == 200:
            result = resp.json()
            print(f"    Status: SUCCESS (200)")
            print(f"    Route: {result.get('route', 'unknown')}")
            print(f"    Confidence: {result.get('confidence_score', 'N/A')}")
            print(f"    Latency: {result.get('latency_seconds', 'N/A')}s")
        else:
            print(f"    Status: ERROR ({resp.status_code})")
            print(f"    Response: {resp.text[:200]}")

    except Exception as e:
        print(f"    ERROR: {e}")

# Step 4: Instructions
print("\n" + "=" * 70)
print("NEXT: CHECK LANGFUSE DASHBOARD")
print("=" * 70)
print("\n1. Open browser: https://cloud.langfuse.com/dashboard")
print("2. Select project: RetailProject (top left dropdown)")
print("3. Click tab: 'Tracing' (left sidebar)")
print("4. You should see traces like:")
print("   - ask_query")
print("   - rag_pipeline")
print("   - sql_query")
print("\n5. Wait 5-10 seconds if traces don't appear immediately")
print("=" * 70)
