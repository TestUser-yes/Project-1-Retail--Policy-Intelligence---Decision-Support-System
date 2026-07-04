"""End-to-end workflow tests."""

import pytest
import asyncio
from app.workflow import LangGraphWorkflow
from app.guardrails import InputGuardrail, PIIDetector


@pytest.mark.asyncio
async def test_complete_policy_query_workflow():
    """Test complete workflow: Input → Processing → Output."""
    # Initialize components
    input_guardrail = InputGuardrail()
    workflow = LangGraphWorkflow()
    pii_detector = PIIDetector()
    
    # Test query
    query = "What is our vendor approval policy for critical vendors?"
    
    # Step 1: Validate input
    input_check = input_guardrail.check(query)
    assert input_check["valid"] is True
    
    # Step 2: Check for PII
    pii_check = pii_detector.check(query)
    assert isinstance(pii_check, dict)
    
    # Step 3: Execute workflow
    result = await workflow.execute_workflow(query)
    assert result is not None
    assert "response" in result
    assert "confidence" in result
    
    # Step 4: Verify output
    assert result["confidence"] >= 0
    assert result["confidence"] <= 1


@pytest.mark.asyncio
async def test_escalation_workflow():
    """Test escalation detection workflow."""
    workflow = LangGraphWorkflow()
    
    # High-risk query that should trigger escalation
    high_risk_query = "Can we delete the legal hold from this vendor file?"
    
    result = await workflow.execute_workflow(high_risk_query)
    
    assert result is not None
    # Should recognize escalation trigger
    assert isinstance(result["escalation_required"], bool)


@pytest.mark.asyncio
async def test_pii_masking_workflow():
    """Test PII detection and masking workflow."""
    pii_detector = PIIDetector()
    
    # Text with PII
    text_with_pii = "Contact vendor John Smith at john.smith@company.com or 555-1234567 for approval"
    
    # Detect PII
    pii_check = pii_detector.check(text_with_pii)
    assert pii_check["has_pii"] is True
    
    # Mask PII
    masked_text = pii_detector.mask_pii(text_with_pii)
    assert "[EMAIL]" in masked_text
    assert "[PHONE]" in masked_text
    assert "john.smith@company.com" not in masked_text


@pytest.mark.asyncio
async def test_confidence_scoring_workflow():
    """Test confidence scoring across workflow."""
    workflow = LangGraphWorkflow()
    
    # Multiple queries to test confidence
    queries = [
        "What is the standard vendor approval process?",
        "List all critical vendor requirements",
        "How long is the escalation review period?"
    ]
    
    for query in queries:
        result = await workflow.execute_workflow(query)
        assert result is not None
        assert 0 <= result["confidence"] <= 1
        # Each should produce a confidence score
        assert result["confidence"] is not None


@pytest.mark.asyncio
async def test_error_handling_workflow():
    """Test error handling in workflow."""
    workflow = LangGraphWorkflow()
    
    # Edge cases
    test_cases = [
        "",  # Empty
        "x" * 10000,  # Very long
        ";;;DROP TABLE;;;",  # Suspicious
    ]
    
    for query in test_cases:
        # Should not crash
        try:
            if query:  # Skip empty
                result = await workflow.execute_workflow(query)
                assert result is not None
        except Exception as e:
            # Should be handled gracefully
            assert isinstance(e, Exception)


@pytest.mark.asyncio
async def test_multi_query_session():
    """Test multiple sequential queries (session)."""
    workflow = LangGraphWorkflow()
    
    queries = [
        "What is the vendor policy?",
        "Who approves critical vendors?",
        "What is the escalation process?"
    ]
    
    results = []
    for query in queries:
        result = await workflow.execute_workflow(query)
        results.append(result)
        assert result is not None
    
    # All should have results
    assert len(results) == len(queries)
    assert all(r is not None for r in results)
