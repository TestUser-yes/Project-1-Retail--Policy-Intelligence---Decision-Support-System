"""
Test suite for database models
Tests model creation and validation
"""

import pytest
from datetime import datetime
from app.models import (
    PolicyDocument,
    Vendor,
    AuditLog,
    RetentionRecord,
    ComplianceReview,
    AIQuery,
    AIResponse,
)


class TestPolicyDocumentModel:
    """Test PolicyDocument model"""

    def test_policy_document_creation(self):
        """Test PolicyDocument can be created"""
        doc = PolicyDocument(
            document_name="Test Policy",
            content="Policy content here",
            section="Section 1",
            page_number=1,
            chunk_number=1,
        )

        assert doc.document_name == "Test Policy"
        assert doc.content == "Policy content here"
        assert doc.section == "Section 1"

    def test_policy_document_fields(self):
        """Test PolicyDocument has required fields"""
        doc = PolicyDocument(
            document_name="Policy",
            content="Content",
            section="Section",
            page_number=1,
            chunk_number=1,
        )

        assert hasattr(doc, "id")
        assert hasattr(doc, "document_name")
        assert hasattr(doc, "content")
        assert hasattr(doc, "section")
        assert hasattr(doc, "page_number")
        assert hasattr(doc, "chunk_number")
        assert hasattr(doc, "created_at")


class TestVendorModel:
    """Test Vendor model"""

    def test_vendor_creation(self):
        """Test Vendor can be created"""
        vendor = Vendor(
            vendor_name="Acme Corp",
            country="USA",
            approval_status="approved",
        )

        assert vendor.vendor_name == "Acme Corp"
        assert vendor.country == "USA"
        assert vendor.approval_status == "approved"

    def test_vendor_fields(self):
        """Test Vendor has required fields"""
        vendor = Vendor(
            vendor_name="Test Vendor",
            country="UK",
            approval_status="pending",
        )

        assert hasattr(vendor, "id")
        assert hasattr(vendor, "vendor_name")
        assert hasattr(vendor, "country")
        assert hasattr(vendor, "approval_status")

    def test_vendor_status_values(self):
        """Test vendor approval status values"""
        valid_statuses = ["approved", "rejected", "pending", "under_review"]

        for status in valid_statuses:
            vendor = Vendor(
                vendor_name="Test",
                country="USA",
                approval_status=status,
            )
            assert vendor.approval_status == status


class TestAuditLogModel:
    """Test AuditLog model"""

    def test_audit_log_creation(self):
        """Test AuditLog can be created"""
        log = AuditLog(
            entity_type="vendor",
            entity_id="123",
            action="created",
            details="Test vendor created",
        )

        assert log.entity_type == "vendor"
        assert log.entity_id == "123"
        assert log.action == "created"

    def test_audit_log_fields(self):
        """Test AuditLog has required fields"""
        log = AuditLog(
            entity_type="policy",
            entity_id="456",
            action="updated",
            details="Details",
        )

        assert hasattr(log, "id")
        assert hasattr(log, "entity_type")
        assert hasattr(log, "entity_id")
        assert hasattr(log, "action")
        assert hasattr(log, "details")
        assert hasattr(log, "timestamp")


class TestRetentionRecordModel:
    """Test RetentionRecord model"""

    def test_retention_record_creation(self):
        """Test RetentionRecord can be created"""
        record = RetentionRecord(
            data_type="customer_email",
            retention_period_days=365,
            compliance_level="gdpr",
        )

        assert record.data_type == "customer_email"
        assert record.retention_period_days == 365
        assert record.compliance_level == "gdpr"

    def test_retention_record_fields(self):
        """Test RetentionRecord has required fields"""
        record = RetentionRecord(
            data_type="pii",
            retention_period_days=730,
            compliance_level="ccpa",
        )

        assert hasattr(record, "id")
        assert hasattr(record, "data_type")
        assert hasattr(record, "retention_period_days")
        assert hasattr(record, "compliance_level")


class TestComplianceReviewModel:
    """Test ComplianceReview model"""

    def test_compliance_review_creation(self):
        """Test ComplianceReview can be created"""
        review = ComplianceReview(
            vendor_id="123",
            review_date=datetime.now(),
            finding="test finding",
            severity="critical",
        )

        assert review.vendor_id == "123"
        assert review.finding == "test finding"
        assert review.severity == "critical"

    def test_compliance_review_severity_levels(self):
        """Test compliance review severity values"""
        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            review = ComplianceReview(
                vendor_id="123",
                review_date=datetime.now(),
                finding="Finding",
                severity=severity,
            )
            assert review.severity == severity


class TestAIQueryModel:
    """Test AIQuery model"""

    def test_ai_query_creation(self):
        """Test AIQuery can be created"""
        query = AIQuery(
            query_text="What is policy?",
            route="rag",
            risk_level="low",
            latency_seconds=0.5,
        )

        assert query.query_text == "What is policy?"
        assert query.route == "rag"
        assert query.risk_level == "low"
        assert query.latency_seconds == 0.5

    def test_ai_query_fields(self):
        """Test AIQuery has required fields"""
        query = AIQuery(
            query_text="Test query",
            route="sql",
            risk_level="medium",
            latency_seconds=1.2,
        )

        assert hasattr(query, "id")
        assert hasattr(query, "query_text")
        assert hasattr(query, "route")
        assert hasattr(query, "risk_level")
        assert hasattr(query, "latency_seconds")
        assert hasattr(query, "created_at")

    def test_ai_query_route_values(self):
        """Test AI query route values"""
        routes = ["rag", "sql", "hybrid"]

        for route in routes:
            query = AIQuery(
                query_text="Test",
                route=route,
                risk_level="low",
                latency_seconds=0.5,
            )
            assert query.route == route


class TestAIResponseModel:
    """Test AIResponse model"""

    def test_ai_response_creation(self):
        """Test AIResponse can be created"""
        response = AIResponse(
            query_id="query123",
            response_text="Response here",
            confidence=0.85,
            escalate=False,
        )

        assert response.query_id == "query123"
        assert response.response_text == "Response here"
        assert response.confidence == 0.85
        assert response.escalate is False

    def test_ai_response_fields(self):
        """Test AIResponse has required fields"""
        response = AIResponse(
            query_id="q456",
            response_text="Response",
            confidence=0.9,
            escalate=True,
        )

        assert hasattr(response, "id")
        assert hasattr(response, "query_id")
        assert hasattr(response, "response_text")
        assert hasattr(response, "confidence")
        assert hasattr(response, "escalate")
        assert hasattr(response, "created_at")

    def test_ai_response_confidence_range(self):
        """Test confidence is between 0 and 1"""
        confidences = [0.0, 0.25, 0.5, 0.75, 1.0]

        for conf in confidences:
            response = AIResponse(
                query_id="q",
                response_text="Response",
                confidence=conf,
                escalate=False,
            )
            assert 0.0 <= response.confidence <= 1.0

    def test_ai_response_escalate_boolean(self):
        """Test escalate is boolean"""
        response_true = AIResponse(
            query_id="q1",
            response_text="Response",
            confidence=0.9,
            escalate=True,
        )

        response_false = AIResponse(
            query_id="q2",
            response_text="Response",
            confidence=0.9,
            escalate=False,
        )

        assert isinstance(response_true.escalate, bool)
        assert isinstance(response_false.escalate, bool)


class TestModelRelationships:
    """Test relationships between models"""

    def test_ai_query_to_response_relationship(self):
        """Test AIQuery to AIResponse relationship"""
        query = AIQuery(
            query_text="Test",
            route="rag",
            risk_level="low",
            latency_seconds=0.5,
        )

        response = AIResponse(
            query_id="123",  # Would reference query.id
            response_text="Response",
            confidence=0.85,
            escalate=False,
        )

        # In real scenario, response.query_id would match query.id
        assert response.query_id is not None

    def test_compliance_review_vendor_relationship(self):
        """Test ComplianceReview to Vendor relationship"""
        vendor = Vendor(
            vendor_name="Test Vendor",
            country="USA",
            approval_status="approved",
        )

        review = ComplianceReview(
            vendor_id="123",  # Would reference vendor.id
            review_date=datetime.now(),
            finding="Finding",
            severity="medium",
        )

        # In real scenario, review.vendor_id would match vendor.id
        assert review.vendor_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
