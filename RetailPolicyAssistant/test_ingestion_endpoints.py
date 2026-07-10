#!/usr/bin/env python3
"""
Test script for ingestion endpoints (/ingest and /retrieve)
Tests Phase 1 (Data Ingestion) and Phase 2 (Data Retrieval) flows
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
DEMO_PDF = "Documents/Anti_Bribery_Ethical_Conduct_Policy.pdf"


def get_token():
    """Get demo auth token."""
    response = requests.get(f"{BASE_URL}/token")
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"❌ Failed to get token: {response.text}")
    return None


def test_ingest_endpoint(token):
    """Test POST /api/ingestion/ingest endpoint."""
    print("\n" + "="*60)
    print("PHASE 1: DATA INGESTION TEST")
    print("="*60)

    if not Path(DEMO_PDF).exists():
        print(f"❌ PDF not found: {DEMO_PDF}")
        return False

    with open(DEMO_PDF, "rb") as f:
        files = {"file": (Path(DEMO_PDF).name, f, "application/pdf")}
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(
            f"{BASE_URL}/api/ingestion/ingest",
            files=files,
            headers=headers
        )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Ingestion successful!")
        print(f"   Filename: {data['filename']}")
        print(f"   Chunks created: {data['chunks_created']}")
        print(f"   Pages: {data['total_pages']}")
        print(f"   Status: {data['status']}")
        print(f"   Timestamp: {data['timestamp']}")
        return True
    else:
        print(f"❌ Ingestion failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def test_retrieve_endpoint(token):
    """Test POST /api/ingestion/retrieve endpoint."""
    print("\n" + "="*60)
    print("PHASE 2: DATA RETRIEVAL TEST")
    print("="*60)

    queries = [
        "What are the ethical conduct policies?",
        "How should employees handle conflicts of interest?",
        "What are the bribery prevention measures?",
    ]

    for query in queries:
        print(f"\n📋 Query: {query}")

        payload = {
            "query": query,
            "k": 3
        }
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(
            f"{BASE_URL}/api/ingestion/retrieve",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['count']} chunks")
            for i, chunk in enumerate(data["chunks"], 1):
                print(f"\n   Chunk {i}:")
                print(f"   - Document: {chunk['metadata']['document_name']}")
                print(f"   - Page: {chunk['metadata']['page_number']}")
                print(f"   - Section: {chunk['metadata']['section']}")
                print(f"   - Content preview: {chunk['content'][:100]}...")
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")


def main():
    print("🚀 Testing Ingestion & Retrieval Endpoints")
    print(f"Base URL: {BASE_URL}")

    # Get auth token
    token = get_token()
    if not token:
        print("❌ Cannot proceed without valid token")
        return

    # Test ingestion
    ingest_success = test_ingest_endpoint(token)
    if not ingest_success:
        print("\n⚠️  Ingestion test failed, skipping retrieval test")
        return

    # Test retrieval
    test_retrieve_endpoint(token)

    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
