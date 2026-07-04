"""Pytest configuration and fixtures."""

import pytest
import asyncio
from app.agents import IntentAgent


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_query():
    """Sample policy query."""
    return "What is the vendor approval policy for critical vendors?"


@pytest.fixture
def sample_user_context():
    """Sample user context."""
    return {
        "user_id": "test-user-123",
        "role": "compliance_officer",
        "department": "Risk Management"
    }


@pytest.fixture
def sample_response():
    """Sample response."""
    return {
        "id": "resp-123",
        "intent": "hybrid",
        "risk_level": "medium",
        "confidence": 0.85,
        "escalation_required": False
    }


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    return IntentAgent()
