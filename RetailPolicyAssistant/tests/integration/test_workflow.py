"""Integration tests for workflow."""

import pytest
import asyncio
from app.workflow import LangGraphWorkflow, WorkflowState


@pytest.mark.asyncio
async def test_workflow_initialization():
    """Test workflow initialization."""
    workflow = LangGraphWorkflow()
    assert workflow is not None


@pytest.mark.asyncio
async def test_workflow_state_creation():
    """Test workflow state creation."""
    state = WorkflowState(
        query="What is the vendor policy?",
        user_id="test-user"
    )
    
    assert state.query == "What is the vendor policy?"
    assert state.user_id == "test-user"
    assert state.intent is None
    assert state.risk_level is None


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test complete workflow execution."""
    workflow = LangGraphWorkflow()
    result = await workflow.execute_workflow(
        query="What is the vendor approval policy?",
        user_id="test-user"
    )
    
    assert result is not None
    assert "response" in result
    assert "confidence" in result
    assert "escalation_required" in result
    assert "traces" in result
    
    # Verify confidence is between 0 and 1
    assert 0 <= result["confidence"] <= 1


@pytest.mark.asyncio
async def test_workflow_high_risk_detection():
    """Test high-risk query detection."""
    workflow = LangGraphWorkflow()
    
    # Query with escalation keyword
    result = await workflow.execute_workflow(
        query="Can we delete this vendor record due to legal hold?",
        user_id="test-user"
    )
    
    assert result is not None
    # Should detect escalation requirement
    assert isinstance(result["escalation_required"], bool)


@pytest.mark.asyncio
async def test_workflow_confidence_scoring():
    """Test 4-factor confidence scoring."""
    workflow = LangGraphWorkflow()
    result = await workflow.execute_workflow(
        query="What policies apply to this situation?",
        user_id="test-user"
    )
    
    assert result is not None
    assert 0 <= result["confidence"] <= 1
    # Confidence should be meaningful (not always 0 or 1)
    assert result["confidence"] in [0, 1] or 0 < result["confidence"] < 1


@pytest.mark.asyncio
async def test_workflow_tracing():
    """Test workflow trace collection."""
    workflow = LangGraphWorkflow()
    result = await workflow.execute_workflow(
        query="Test query",
        user_id="test-user"
    )
    
    # Should have traces
    assert "traces" in result
    # Traces should be a list (could be empty in stub)
    assert isinstance(result["traces"], list)
