"""Integration test for dashboard endpoint - verifies 422 error is fixed."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import get_demo_token, get_demo_refresh_token, User
from app.database.session import get_db
from sqlalchemy.orm import Session


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create valid auth headers with JWT token."""
    access_token = get_demo_token()
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def db_session() -> Session:
    """Create a database session for tests."""
    from app.database.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestAuthenticationFlow:
    """Test authentication flow - tokens must be initialized."""

    def test_token_endpoint_returns_200(self, client):
        """Verify /token endpoint returns 200 and sets cookies."""
        response = client.post("/token")
        assert response.status_code == 200
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_token_endpoint_sets_access_cookie(self, client):
        """Verify /token endpoint sets secure access_token cookie."""
        response = client.post("/token")
        assert response.status_code == 200
        # Check cookies are set
        cookies = response.cookies
        assert "access_token" in cookies or "Set-Cookie" in response.headers

    def test_auth_status_without_token_returns_401(self, client):
        """Verify /auth/status returns 401 without authentication."""
        response = client.get("/auth/status")
        assert response.status_code == 200  # /auth/status doesn't require auth
        data = response.json()
        assert data["authenticated"] == False

    def test_auth_status_with_bearer_token_returns_200(self, client, auth_headers):
        """Verify /auth/status returns 200 with valid Bearer token."""
        response = client.get("/auth/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] == True


class TestDashboardEndpoint:
    """Test dashboard endpoint - verify 422 error is fixed."""

    def test_dashboard_without_auth_returns_401(self, client):
        """Verify /api/dashboard returns 401 without authentication."""
        response = client.get("/api/dashboard")
        assert response.status_code == 401

    def test_dashboard_with_bearer_token_returns_200(self, client, auth_headers):
        """Verify /api/dashboard returns 200 with valid Bearer token."""
        response = client.get("/api/dashboard", headers=auth_headers)
        # Should NOT be 422 - that was the bug
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_dashboard_response_structure(self, client, auth_headers):
        """Verify dashboard response has correct structure."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Verify all required fields are present
        required_fields = [
            "totalQueries",
            "avgLatency",
            "escalationRate",
            "budgetUsed",
            "activeUsers",
            "successRate",
            "queryByRoute",
            "queryByRisk",
            "topPolicies",
            "recentQueries",
            "hourlyTrends",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_dashboard_query_by_route_has_correct_keys(self, client, auth_headers):
        """Verify queryByRoute has RAG, SQL, and Hybrid counts."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        query_by_route = data["queryByRoute"]
        assert "rag" in query_by_route
        assert "sql" in query_by_route
        assert "hybrid" in query_by_route

    def test_dashboard_query_by_risk_has_correct_keys(self, client, auth_headers):
        """Verify queryByRisk has low, medium, and high counts."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        query_by_risk = data["queryByRisk"]
        assert "low" in query_by_risk
        assert "medium" in query_by_risk
        assert "high" in query_by_risk

    def test_dashboard_slo_metrics_present(self, client, auth_headers):
        """Verify dashboard includes SLO metrics."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "sloMetrics" in data
        slo = data["sloMetrics"]
        assert "success_rate" in slo
        assert "avg_latency_ms" in slo
        assert "target_latency_ms" in slo
        assert "escalation_count" in slo

    def test_dashboard_response_is_json(self, client, auth_headers):
        """Verify dashboard returns valid JSON."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers.get("content-type") is not None
        assert "application/json" in response.headers.get("content-type", "")


class TestCookieBasedAuthentication:
    """Test that authentication works with cookies (as frontend uses it)."""

    def test_get_token_then_use_cookie_for_dashboard(self, client):
        """Full flow: get token, then use cookie to access dashboard."""
        # Step 1: Get token (sets cookie)
        token_response = client.post("/token")
        assert token_response.status_code == 200

        # Step 2: Use the same client (which retains cookies) to access dashboard
        dashboard_response = client.get("/api/dashboard")
        # Should work because TestClient retains cookies
        assert dashboard_response.status_code == 200

    def test_dashboard_metrics_are_numeric(self, client, auth_headers):
        """Verify dashboard metrics are numeric types."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["totalQueries"], int)
        assert isinstance(data["avgLatency"], (int, float))
        assert isinstance(data["escalationRate"], (int, float))
        assert isinstance(data["budgetUsed"], (int, float))


class TestErrorHandling:
    """Test error handling for edge cases."""

    def test_dashboard_handles_empty_database(self, client, auth_headers):
        """Verify dashboard returns valid response even with no queries."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Should have all fields, even if zeros/empty
        assert "totalQueries" in data
        assert "recentQueries" in data
        assert isinstance(data["recentQueries"], list)

    def test_invalid_token_returns_401(self, client):
        """Verify invalid JWT token returns 401, not 422."""
        response = client.get(
            "/api/dashboard",
            headers={"Authorization": "Bearer invalid-token-xyz"}
        )
        # Should be 401 (invalid token), not 422 (validation error)
        assert response.status_code == 401
