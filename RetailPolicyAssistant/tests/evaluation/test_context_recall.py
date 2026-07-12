"""Unit tests for Context Recall Evaluator."""

import pytest
from app.evaluation.context_recall import ContextRecallEvaluator


@pytest.fixture
def evaluator():
    """Create a fresh evaluator for each test."""
    return ContextRecallEvaluator()


class TestContextRecall:
    """Test Context Recall evaluation."""

    def test_empty_chunks_returns_zero(self, evaluator):
        """Recall should be 0.0 for empty chunk list."""
        score = evaluator.evaluate_recall("test query", [], "rag")
        assert score == 0.0

    def test_single_chunk_acceptable(self, evaluator):
        """Single chunk should return acceptable score."""
        chunks = [
            {
                "content": "test content",
                "document": "test.pdf",
                "section": "Section"
            }
        ]
        score = evaluator.evaluate_recall("test query", chunks, "rag")
        assert 0.6 <= score <= 0.8

    def test_diverse_documents_better_recall(self, evaluator):
        """Multiple documents should improve recall."""
        chunks_single_doc = [
            {"content": "content1", "document": "test.pdf", "section": "S1"},
            {"content": "content2", "document": "test.pdf", "section": "S2"},
            {"content": "content3", "document": "test.pdf", "section": "S3"},
        ]
        chunks_multi_doc = [
            {"content": "content1", "document": "test1.pdf", "section": "S1"},
            {"content": "content2", "document": "test2.pdf", "section": "S2"},
            {"content": "content3", "document": "test3.pdf", "section": "S3"},
        ]
        score_single = evaluator.evaluate_recall("query", chunks_single_doc, "rag")
        score_multi = evaluator.evaluate_recall("query", chunks_multi_doc, "rag")
        assert score_multi > score_single

    def test_diverse_sections_better_recall(self, evaluator):
        """Multiple sections should improve recall."""
        chunks_same_section = [
            {"content": "content1", "document": "test.pdf", "section": "Introduction"},
            {"content": "content2", "document": "test.pdf", "section": "Introduction"},
            {"content": "content3", "document": "test.pdf", "section": "Introduction"},
        ]
        chunks_diff_sections = [
            {"content": "content1", "document": "test.pdf", "section": "Introduction"},
            {"content": "content2", "document": "test.pdf", "section": "Details"},
            {"content": "content3", "document": "test.pdf", "section": "Conclusion"},
        ]
        score_same = evaluator.evaluate_recall("query", chunks_same_section, "rag")
        score_diff = evaluator.evaluate_recall("query", chunks_diff_sections, "rag")
        assert score_diff > score_same

    def test_duplicate_content_penalty(self, evaluator):
        """Similar/duplicate content should reduce recall."""
        chunks_diverse = [
            {"content": "unique first content about topic", "document": "test1.pdf", "section": "S1"},
            {"content": "unique second content about topic", "document": "test2.pdf", "section": "S2"},
            {"content": "unique third content about topic", "document": "test3.pdf", "section": "S3"},
        ]
        chunks_duplicate = [
            {"content": "same content repeated same content repeated", "document": "test1.pdf", "section": "S1"},
            {"content": "same content repeated same content repeated", "document": "test2.pdf", "section": "S2"},
            {"content": "same content repeated same content repeated", "document": "test3.pdf", "section": "S3"},
        ]
        score_diverse = evaluator.evaluate_recall("query", chunks_diverse, "rag")
        score_dup = evaluator.evaluate_recall("query", chunks_duplicate, "rag")
        assert score_diverse > score_dup

    def test_sql_route_vendor_coverage(self, evaluator):
        """SQL route should prefer vendor data."""
        query = "vendor requirements"
        chunks_vendor = [
            {"content": "vendor requirements", "document": "vendor_contract.pdf", "section": "Requirements"},
            {"content": "more vendor data", "document": "vendor_sla.pdf", "section": "SLA"},
        ]
        score = evaluator.evaluate_recall(query, chunks_vendor, "sql")
        assert score > 0.6

    def test_sql_route_policy_coverage(self, evaluator):
        """SQL route should also accept policy data."""
        query = "data policy requirements"
        chunks_policy = [
            {"content": "data policy", "document": "policy.pdf", "section": "Policy"},
        ]
        score = evaluator.evaluate_recall(query, chunks_policy, "sql")
        assert score > 0.5

    def test_rag_route_diversity(self, evaluator):
        """RAG route should favor diverse content sources."""
        query = "comprehensive information"
        chunks = [
            {"content": "introduction content", "document": "doc1.pdf", "section": "Intro"},
            {"content": "details content", "document": "doc2.pdf", "section": "Details"},
            {"content": "conclusion content", "document": "doc3.pdf", "section": "Conclusion"},
            {"content": "additional content", "document": "doc4.pdf", "section": "Additional"},
            {"content": "reference content", "document": "doc5.pdf", "section": "References"},
            {"content": "appendix content", "document": "doc6.pdf", "section": "Appendix"},
        ]
        score = evaluator.evaluate_recall(query, chunks, "rag")
        # Should be high for diverse multi-document retrieval
        assert score > 0.75

    def test_hybrid_route_balanced(self, evaluator):
        """Hybrid route should balance both strategies."""
        query = "policy and vendor data"
        chunks = [
            {"content": "policy data", "document": "policy.pdf", "section": "Policy"},
            {"content": "vendor data", "document": "vendor.pdf", "section": "Vendor"},
        ]
        score = evaluator.evaluate_recall(query, chunks, "hybrid")
        # Should be reasonable for balanced coverage
        assert 0.5 <= score <= 0.9

    def test_score_clamped_to_range(self, evaluator):
        """Score should always be between 0.0 and 1.0."""
        routes = ["rag", "sql", "hybrid"]
        for route in routes:
            chunks = [
                {"content": "content", "document": f"doc{i}.pdf", "section": f"S{i}"}
                for i in range(5)
            ]
            score = evaluator.evaluate_recall("query", chunks, route)
            assert 0.0 <= score <= 1.0

    def test_document_count_effect(self, evaluator):
        """More documents should generally improve recall."""
        query = "comprehensive coverage"
        # Few documents
        chunks_few = [
            {"content": "content1", "document": "doc1.pdf", "section": "S1"},
            {"content": "content2", "document": "doc2.pdf", "section": "S2"},
        ]
        # Many documents
        chunks_many = [
            {"content": f"content{i}", "document": f"doc{i}.pdf", "section": f"S{i}"}
            for i in range(6)
        ]
        score_few = evaluator.evaluate_recall(query, chunks_few, "rag")
        score_many = evaluator.evaluate_recall(query, chunks_many, "rag")
        assert score_many > score_few
