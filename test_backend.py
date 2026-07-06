#!/usr/bin/env python3
"""Quick test of the backend API."""

import sys
import time
import requests
import json

# Test data
TEST_QUERY = "What is our data retention policy for customer records?"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_token():
    """Get demo token."""
    print("\n" + "="*70)
    print("TEST 2: Get Demo Token")
    print("="*70)
    try:
        resp = requests.get("http://localhost:8000/token", timeout=5)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Token: {data.get('access_token', 'N/A')[:20]}...")
        return data.get("access_token") if resp.status_code == 200 else None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_ask_query(token):
    """Test the main ask endpoint."""
    print("\n" + "="*70)
    print("TEST 3: Ask Query")
    print("="*70)
    print(f"Query: {TEST_QUERY}")
    print("-"*70)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": TEST_QUERY,
    }

    try:
        resp = requests.post(
            "http://localhost:8000/ask",
            json=payload,
            headers=headers,
            timeout=30
        )
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"\n✅ Query Result:")
            print(f"  Route: {data.get('route')}")
            print(f"  Risk Level: {data['risk'].get('risk_level')}")
            print(f"  Confidence: {data.get('confidence_score', 0)}")
            print(f"  Answer: {data['result']['result'][:200]}...")
            return True
        else:
            print(f"❌ Error: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("BACKEND SYSTEM TEST")
    print("="*70)

    # Wait for server to be ready
    for i in range(5):
        try:
            requests.get("http://localhost:8000/health", timeout=2)
            break
        except:
            if i < 4:
                print(f"Waiting for server... ({i+1}/5)")
                time.sleep(1)

    # Run tests
    health_ok = test_health()
    token = test_token()

    if health_ok and token:
        query_ok = test_ask_query(token)
    else:
        query_ok = False
        print("\n⚠️  Skipping query test due to earlier failures")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Token Retrieval: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Query Execution: {'✅ PASS' if query_ok else '❌ FAIL'}")
    print("="*70 + "\n")

    return 0 if (health_ok and token and query_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
