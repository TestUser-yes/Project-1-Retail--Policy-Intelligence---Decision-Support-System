"""
Pytest configuration and fixtures
Shared setup for all tests
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        "test_database_url": "sqlite:///:memory:",
        "test_timeout": 30,
        "test_debug": True,
    }


@pytest.fixture
def sample_query():
    """Provide a sample query for testing"""
    return "What is our data retention policy?"


@pytest.fixture
def sample_vendor_query():
    """Provide a sample vendor query"""
    return "List vendors with critical findings"


@pytest.fixture
def sample_high_risk_query():
    """Provide a sample high-risk query"""
    return "Delete compliance records?"


@pytest.fixture
def sample_policy_content():
    """Provide sample policy content"""
    return """
    Data Retention Policy

    1. Customer email data should be retained for 365 days
    2. All audit logs must be retained for 7 years
    3. PII must be encrypted and securely stored
    4. Restricted jurisdiction vendors require special approval
    """


@pytest.fixture
def sample_vendor_data():
    """Provide sample vendor data"""
    return {
        "vendor_name": "Acme Supplies",
        "country": "USA",
        "approval_status": "approved",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Hooks for test output
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add markers based on test names
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
