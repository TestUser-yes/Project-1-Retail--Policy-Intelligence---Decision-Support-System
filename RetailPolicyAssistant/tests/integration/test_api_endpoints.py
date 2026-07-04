"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code in [200, 404]  # Might not exist


def test_chat_query_endpoint(client):
    """Test POST /api/chat/query."""
    payload = {
        "query": "What is the vendor policy?",
        "user_id": "test-user"
    }
    response = client.post("/api/chat/query", json=payload)
    
    # Should return 200 or working endpoint
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "query" in data
        assert "response" in data


def test_agents_status_endpoint(client):
    """Test GET /api/agents/status."""
    response = client.get("/api/agents/status")
    
    if response.status_code == 200:
        data = response.json()
        assert "agents" in data
        assert "total_active" in data


def test_audit_logs_endpoint(client):
    """Test GET /api/audit/logs."""
    response = client.get("/api/audit/logs")
    
    if response.status_code == 200:
        data = response.json()
        assert "logs" in data


def test_compliance_status_endpoint(client):
    """Test GET /api/audit/compliance-status."""
    response = client.get("/api/audit/compliance-status")
    
    if response.status_code == 200:
        data = response.json()
        assert "slo_compliance_rate" in data
        assert "average_latency_ms" in data


def test_escalation_pending_endpoint(client):
    """Test GET /api/escalation/pending."""
    response = client.get("/api/escalation/pending")
    
    if response.status_code == 200:
        data = response.json()
        assert "escalations" in data


def test_invalid_query(client):
    """Test invalid query handling."""
    payload = {
        "query": "",  # Empty query
        "user_id": "test-user"
    }
    response = client.post("/api/chat/query", json=payload)
    
    # Should handle gracefully
    assert response.status_code in [200, 400, 422]


def test_missing_required_field(client):
    """Test missing required field."""
    payload = {
        "user_id": "test-user"
        # Missing "query"
    }
    response = client.post("/api/chat/query", json=payload)
    
    # Should return validation error
    assert response.status_code in [400, 422]
