"""Unit tests for Context Precision Evaluator."""

import pytest
from app.evaluation.context_precision import ContextPrecisionEvaluator


@pytest.fixture
def evaluator():
    """Create a fresh evaluator for each test."""
    return ContextPrecisionEvaluator()


class TestContextPrecision:
    """Test Context Precision evaluation."""

    def test_empty_chunks_returns_zero(self, evaluator):
        """Precision should be 0.0 for empty chunk list."""
        score = evaluator.evaluate_precision("test query", [], "rag")
        assert score == 0.0

    def test_empty_query_returns_default(self, evaluator):
        """Empty query should return default score."""
        chunks = [{"content": "test content", "document": "test.pdf", "section": "Introduction"}]
        score = evaluator.evaluate_precision("", chunks, "rag")
        assert 0.5 <= score <= 0.7

    def test_perfect_keyword_match(self, evaluator):
        """High score when query keywords match chunk content."""
        query = "data retention policy"
        chunks = [
            {
                "content": "Our data retention policy requires storing customer data for 7 years",
                "document": "data_retention.pdf",
                "section": "Retention Policy"
            }
        ]
        score = evaluator.evaluate_precision(query, chunks, "rag")
        assert score > 0.7  # High precision for relevant content

    def test_poor_keyword_match(self, evaluator):
        """Low score when query keywords don't match chunk content."""
        query = "vendor compliance requirements"
        chunks = [
            {
                "content": "Lorem ipsum dolor sit amet consectetur adipiscing elit",
                "document": "random.pdf",
                "section": "Random"
            }
        ]
        score = evaluator.evaluate_precision(query, chunks, "rag")
        assert score < 0.5  # Low precision for irrelevant content

    def test_section_relevance_boost(self, evaluator):
        """Section matching should boost score."""
        query = "policy requirements"
        chunks_good = [
            {
                "content": "generic text about something",
                "document": "document.pdf",
                "section": "Policy Requirements"
            }
        ]
        chunks_bad = [
            {
                "content": "generic text about something",
                "document": "document.pdf",
                "section": "Random Section"
            }
        ]
        score_good = evaluator.evaluate_precision(query, chunks_good, "rag")
        score_bad = evaluator.evaluate_precision(query, chunks_bad, "rag")
        assert score_good > score_bad

    def test_document_type_boost_sql(self, evaluator):
        """SQL route should boost vendor/contract documents."""
        query = "vendor requirements"
        chunks_vendor = [
            {
                "content": "vendor text",
                "document": "vendor_contract.pdf",
                "section": "Section"
            }
        ]
        chunks_policy = [
            {
                "content": "policy text",
                "document": "data_policy.pdf",
                "section": "Section"
            }
        ]
        score_vendor = evaluator.evaluate_precision(query, chunks_vendor, "sql")
        score_policy = evaluator.evaluate_precision(query, chunks_policy, "sql")
        assert score_vendor > score_policy

    def test_document_type_boost_rag(self, evaluator):
        """RAG route should boost policy documents."""
        query = "policy requirements"
        chunks_policy = [
            {
                "content": "policy text",
                "document": "data_policy.pdf",
                "section": "Policy"
            }
        ]
        chunks_vendor = [
            {
                "content": "vendor text",
                "document": "vendor_contract.pdf",
                "section": "Contract"
            }
        ]
        score_policy = evaluator.evaluate_precision(query, chunks_policy, "rag")
        score_vendor = evaluator.evaluate_precision(query, chunks_vendor, "rag")
        assert score_policy > score_vendor

    def test_multiple_chunks_average(self, evaluator):
        """Score should be average of chunk relevances."""
        query = "retention policy"
        chunks = [
            {
                "content": "retention policy for 7 years",
                "document": "retention.pdf",
                "section": "Policy"
            },
            {
                "content": "random unrelated content about cats",
                "document": "random.pdf",
                "section": "Random"
            }
        ]
        score = evaluator.evaluate_precision(query, chunks, "rag")
        # Should be between irrelevant (low) and relevant (high)
        assert 0.3 <= score <= 0.8

    def test_score_clamped_to_range(self, evaluator):
        """Score should always be between 0.0 and 1.0."""
        queries = ["test", "policy", "vendor", "compliance", "retention"]
        for query in queries:
            chunks = [{"content": "any content", "document": "test.pdf", "section": "Section"}]
            score = evaluator.evaluate_precision(query, chunks, "rag")
            assert 0.0 <= score <= 1.0

    def test_hybrid_route_combines_factors(self, evaluator):
        """Hybrid route should balance policy and vendor factors."""
        query = "policy and vendor requirements"
        chunks = [
            {
                "content": "policy and vendor requirements text",
                "document": "combined.pdf",
                "section": "Requirements"
            }
        ]
        score = evaluator.evaluate_precision(query, chunks, "hybrid")
        # Should be fairly high for content matching both
        assert score > 0.5
