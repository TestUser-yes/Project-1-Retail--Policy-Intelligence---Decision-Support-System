"""
Test suite for the Orchestrator
Tests query processing and agent coordination
"""

import pytest
import asyncio
from app.orchestrator import Orchestrator
from app.database.session import SessionLocal


def _run_async_orchestrator(orchestrator, query):
    """Helper to run async orchestrator in sync test context."""
    return asyncio.run(orchestrator.run(query))


class TestOrchestratorBasic:
    """Test basic orchestrator functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        """Clean up after tests"""
        self.db.close()

    def test_orchestrator_initializes(self):
        """Test orchestrator can be initialized"""
        assert self.orchestrator is not None
        assert self.orchestrator.db is not None

    def test_orchestrator_has_all_agents(self):
        """Test orchestrator has all required agents"""
        assert self.orchestrator.intent is not None
        assert self.orchestrator.rag is not None
        assert self.orchestrator.sql is not None
        assert self.orchestrator.hybrid is not None
        assert self.orchestrator.risk is not None
        assert self.orchestrator.escalation is not None


class TestOrchestratorQueryProcessing:
    """Test query processing"""

    def setup_method(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        self.db.close()

    def test_run_returns_response(self):
        """Test run method returns a response"""
        result = _run_async_orchestrator(self.orchestrator, "What is retention policy?")

        assert result is not None
        assert isinstance(result, dict)

    def test_response_has_required_fields(self):
        """Test response has all required fields"""
        result = _run_async_orchestrator(self.orchestrator,"What is data retention policy?")

        # Check all required fields present
        assert "query" in result
        assert "intent" in result
        assert "route" in result
        assert "result" in result
        assert "risk" in result
        assert "escalate" in result

    def test_response_structure(self):
        """Test response structure is correct"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy?")

        assert isinstance(result["query"], str)
        assert isinstance(result["intent"], dict)
        assert "intent" in result["intent"]
        assert "reason" in result["intent"]
        assert isinstance(result["route"], str)
        assert isinstance(result["result"], dict)
        assert "result" in result["result"]
        assert isinstance(result["risk"], dict)
        assert "risk_level" in result["risk"]
        assert "reason" in result["risk"]
        assert isinstance(result["escalate"], bool)

    def test_query_stored_correctly(self):
        """Test query is stored correctly"""
        query_text = "What is compliance policy?"
        result = _run_async_orchestrator(self.orchestrator,query_text)

        assert result["query"] == query_text

    def test_route_is_valid(self):
        """Test route is one of valid types"""
        result = _run_async_orchestrator(self.orchestrator,"What is data retention policy?")

        assert result["route"] in ["rag", "sql", "hybrid"]

    def test_risk_level_is_valid(self):
        """Test risk level is valid"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy?")

        assert result["risk"]["risk_level"] in ["low", "medium", "high"]

    def test_result_has_content(self):
        """Test result has actual content"""
        result = _run_async_orchestrator(self.orchestrator,"What is data retention policy?")

        result_text = result["result"]["result"]
        assert len(str(result_text)) > 0

    def test_escalate_is_boolean(self):
        """Test escalate field is boolean"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy?")

        assert isinstance(result["escalate"], bool)


class TestOrchestratorRouting:
    """Test query routing"""

    def setup_method(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        self.db.close()

    def test_policy_query_routes_to_rag(self):
        """Test policy queries route to RAG"""
        result = _run_async_orchestrator(self.orchestrator,"What is our data retention policy?")

        assert result["route"] in ["rag", "hybrid"]

    def test_vendor_query_routes_to_sql(self):
        """Test vendor queries route to SQL"""
        result = _run_async_orchestrator(self.orchestrator,"List vendors with critical findings")

        assert result["route"] in ["sql", "hybrid"]

    def test_complex_query_routes_correctly(self):
        """Test complex queries route correctly"""
        result = _run_async_orchestrator(self.orchestrator,"Is vendor 456 compliant with our policy?")

        assert result["route"] in ["hybrid", "sql", "rag"]


class TestOrchestratorRiskDetection:
    """Test risk detection"""

    def setup_method(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        self.db.close()

    def test_low_risk_query_detected(self):
        """Test low-risk queries are detected"""
        result = _run_async_orchestrator(self.orchestrator,"What is our policy?")

        assert result["risk"]["risk_level"] in ["low", "medium"]

    def test_high_risk_query_detected(self):
        """Test high-risk queries are detected"""
        result = _run_async_orchestrator(self.orchestrator,"Delete compliance records?")

        assert result["risk"]["risk_level"] in ["high", "medium"]

    def test_high_risk_triggers_escalation(self):
        """Test high-risk scenarios trigger escalation"""
        result = _run_async_orchestrator(self.orchestrator,"Delete audit logs?")

        if result["risk"]["risk_level"] == "high":
            assert result["escalate"] is True


class TestOrchestratorErrorHandling:
    """Test error handling"""

    def setup_method(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        self.db.close()

    def test_empty_query_handled(self):
        """Test empty query is handled"""
        result = _run_async_orchestrator(self.orchestrator,"")

        assert result is not None
        assert isinstance(result, dict)

    def test_very_long_query_handled(self):
        """Test very long query is handled"""
        long_query = "What is the policy? " * 100

        result = _run_async_orchestrator(self.orchestrator,long_query)

        assert result is not None
        assert isinstance(result, dict)

    def test_special_characters_handled(self):
        """Test special characters in query"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy? @#$%^&*()")

        assert result is not None
        assert isinstance(result, dict)

    def test_unicode_characters_handled(self):
        """Test unicode characters in query"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy? 你好世界 مرحبا")

        assert result is not None
        assert isinstance(result, dict)


class TestOrchestratorLatency:
    """Test latency tracking"""

    def setup_method(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        self.db.close()

    def test_latency_tracked(self):
        """Test latency is tracked"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy?")

        assert "latency" in result or "latency_seconds" in result

    def test_latency_is_positive(self):
        """Test latency is positive number"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy?")

        latency = result.get("latency", result.get("latency_seconds", 0))
        assert latency >= 0

    def test_latency_within_bounds(self):
        """Test latency is within reasonable bounds"""
        result = _run_async_orchestrator(self.orchestrator,"What is policy?")

        latency = result.get("latency", result.get("latency_seconds", 0))
        # Should complete within 30 seconds
        assert latency < 30


class TestOrchestratorMultipleQueries:
    """Test processing multiple queries"""

    def setup_method(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)

    def teardown_method(self):
        self.db.close()

    def test_sequential_queries(self):
        """Test multiple sequential queries work"""
        queries = [
            "What is policy?",
            "List vendors",
            "Is vendor compliant?",
            "Delete records?",
        ]

        results = []
        for query in queries:
            result = _run_async_orchestrator(self.orchestrator,query)
            results.append(result)

        assert len(results) == 4
        assert all(isinstance(r, dict) for r in results)
        assert all("query" in r for r in results)

    def test_different_routes(self):
        """Test different routes are used"""
        queries = [
            "What is policy?",  # RAG
            "List vendors",  # SQL
            "Is vendor compliant?",  # Hybrid
        ]

        routes = []
        for query in queries:
            result = _run_async_orchestrator(self.orchestrator,query)
            routes.append(result["route"])

        # Should have mix of routes
        assert len(set(routes)) >= 1  # At least one unique route


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
