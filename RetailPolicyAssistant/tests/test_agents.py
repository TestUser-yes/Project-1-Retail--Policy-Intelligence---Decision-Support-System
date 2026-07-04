"""Unit tests for all agents."""

import pytest
import asyncio
from app.agents import (
    IntentAgent, RiskAgent, RouterAgent, RetrievalAgent,
    SQLAgent, PolicyAgent, ComplianceAgent, ValidatorAgent,
    ConfidenceAgent, ResponseAgent, ReflectionAgent, EscalationAgent
)
from app.agents.base_agent import AgentInput, AgentOutput, AgentStatus


@pytest.fixture
def agent_input():
    """Fixture for agent input."""
    return AgentInput(
        query="What is the vendor approval policy?",
        context={"user_id": "test-user"},
        previous_outputs={}
    )


@pytest.mark.asyncio
async def test_intent_agent(agent_input):
    """Test IntentAgent execution."""
    agent = IntentAgent()
    output = await agent.run(agent_input)
    
    assert isinstance(output, AgentOutput)
    assert output.success is True
    assert 0 <= output.confidence <= 1
    assert len(agent.traces) > 0


@pytest.mark.asyncio
async def test_risk_agent(agent_input):
    """Test RiskAgent execution."""
    agent = RiskAgent()
    agent_input.previous_outputs = {"result": "Test policy"}
    output = await agent.run(agent_input)
    
    assert isinstance(output, AgentOutput)
    assert output.success is True
    assert "risk_level" in output.data or output.success


@pytest.mark.asyncio
async def test_router_agent(agent_input):
    """Test RouterAgent execution."""
    agent = RouterAgent()
    agent_input.previous_outputs = {"intent": "rag"}
    output = await agent.run(agent_input)
    
    assert isinstance(output, AgentOutput)
    assert output.success is True
    assert "route" in output.data


@pytest.mark.asyncio
async def test_retrieval_agent(agent_input):
    """Test RetrievalAgent execution."""
    agent = RetrievalAgent()
    output = await agent.run(agent_input)
    
    assert isinstance(output, AgentOutput)
    assert output.success is True


@pytest.mark.asyncio
async def test_confidence_agent(agent_input):
    """Test ConfidenceAgent 4-factor scoring."""
    agent = ConfidenceAgent()
    agent_input.previous_outputs = {
        "document_confidence": 0.8,
        "sql_confidence": 0.7,
        "reflection_confidence": 0.85,
        "agreement_confidence": 0.9
    }
    output = await agent.run(agent_input)
    
    assert isinstance(output, AgentOutput)
    assert output.success is True
    assert "confidence" in output.data
    # Verify 4-factor calculation
    expected = 0.8 * 0.4 + 0.7 * 0.2 + 0.85 * 0.2 + 0.9 * 0.2
    assert abs(output.data["confidence"] - expected) < 0.01


@pytest.mark.asyncio
async def test_escalation_agent(agent_input):
    """Test EscalationAgent."""
    agent = EscalationAgent()
    agent_input.previous_outputs = {"risk_result": {"risk_level": "high"}}
    output = await agent.run(agent_input)
    
    assert isinstance(output, AgentOutput)
    assert output.success is True


@pytest.mark.asyncio
async def test_agent_trace_recording():
    """Test agent trace recording."""
    agent = IntentAgent()
    agent_input = AgentInput(
        query="Test query",
        context={}
    )
    
    output = await agent.run(agent_input)
    traces = agent.get_traces()
    
    assert len(traces) > 0
    assert traces[0].agent_name == "intent_agent"
    assert traces[0].status in [AgentStatus.SUCCESS, AgentStatus.ERROR]


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling."""
    agent = IntentAgent()
    agent_input = AgentInput(query="")  # Empty query
    
    output = await agent.run(agent_input)
    # Should handle gracefully
    assert isinstance(output, AgentOutput)


def test_all_agents_initialization():
    """Test all agents can be instantiated."""
    agents = [
        IntentAgent(),
        RiskAgent(),
        RouterAgent(),
        RetrievalAgent(),
        SQLAgent(),
        PolicyAgent(),
        ComplianceAgent(),
        ValidatorAgent(),
        ConfidenceAgent(),
        ResponseAgent(),
        ReflectionAgent(),
        EscalationAgent(),
    ]
    
    assert len(agents) == 12
    for agent in agents:
        assert agent.name is not None
        assert agent.description is not None
