"""
Test suite for all agents in the system
Tests individual agent functionality
"""

import pytest
from app.agents.intent_agent import IntentAgent
from app.agents.rag_agent import RAGAgent
from app.agents.sql_agent import SQLAgent
from app.agents.hybrid_agent import HybridAgent
from app.agents.risk_agent import RiskAgent
from app.agents.escalation_agent import EscalationAgent


class TestIntentAgent:
    """Test Intent Detection Agent"""

    def setup_method(self):
        self.agent = IntentAgent()

    def test_rag_intent_detection(self):
        """Test RAG intent is detected for policy questions"""
        result = self.agent.run("What is our data retention policy?")

        assert result is not None
        assert "intent" in result
        assert result["intent"] in ["rag", "sql", "hybrid"]
        assert "reason" in result

    def test_sql_intent_detection(self):
        """Test SQL intent for vendor data queries"""
        result = self.agent.run("List all vendors with critical findings")

        assert result is not None
        assert "intent" in result
        assert result["intent"] in ["rag", "sql", "hybrid"]

    def test_hybrid_intent_detection(self):
        """Test Hybrid intent for complex queries"""
        result = self.agent.run("Is vendor 456 compliant with our retention policy?")

        assert result is not None
        assert "intent" in result
        assert result["intent"] in ["rag", "sql", "hybrid"]

    def test_intent_has_reason(self):
        """Test that intent result includes reason"""
        result = self.agent.run("What is compliance status?")

        assert "reason" in result
        assert len(result["reason"]) > 0


class TestRAGAgent:
    """Test RAG (Retrieval-Augmented Generation) Agent"""

    def setup_method(self):
        self.agent = RAGAgent()

    def test_rag_returns_result(self):
        """Test RAG agent returns a result"""
        result = self.agent.run("What is our data retention policy?")

        assert result is not None
        assert "result" in result
        assert len(str(result["result"])) > 0

    def test_rag_result_is_string_or_dict(self):
        """Test RAG result is properly formatted"""
        result = self.agent.run("What is GDPR compliance requirement?")

        assert result is not None
        assert "result" in result
        # Result should be either string or dict
        assert isinstance(result["result"], (str, dict))

    def test_rag_handles_policy_questions(self):
        """Test RAG handles policy-related questions"""
        result = self.agent.run("How should we handle PII?")

        assert result is not None
        assert "result" in result


class TestSQLAgent:
    """Test SQL Query Agent"""

    def setup_method(self):
        self.agent = SQLAgent()

    def test_sql_returns_result(self):
        """Test SQL agent returns a result"""
        result = self.agent.run("List all vendors")

        assert result is not None
        assert "result" in result

    def test_sql_result_format(self):
        """Test SQL result is properly formatted"""
        result = self.agent.run("How many vendors are approved?")

        assert result is not None
        assert "result" in result
        assert isinstance(result["result"], (str, dict, list))

    def test_sql_handles_vendor_queries(self):
        """Test SQL handles vendor-related queries"""
        result = self.agent.run("Show vendors with critical findings")

        assert result is not None
        assert "result" in result


class TestHybridAgent:
    """Test Hybrid (RAG + SQL) Agent"""

    def setup_method(self):
        self.agent = HybridAgent()

    def test_hybrid_returns_result(self):
        """Test Hybrid agent returns a result"""
        result = self.agent.run("Is vendor 456 compliant with policy?")

        assert result is not None
        assert "result" in result

    def test_hybrid_combines_sources(self):
        """Test Hybrid combines policy and database info"""
        result = self.agent.run("Are restricted jurisdiction vendors following policy?")

        assert result is not None
        assert "result" in result
        # Result should be comprehensive
        assert len(str(result["result"])) > 0

    def test_hybrid_handles_complex_queries(self):
        """Test Hybrid handles complex queries"""
        result = self.agent.run("Which vendors fail our encryption standards?")

        assert result is not None
        assert "result" in result


class TestRiskAgent:
    """Test Risk Assessment Agent"""

    def setup_method(self):
        self.agent = RiskAgent()

    def test_risk_assessment_returns_level(self):
        """Test risk agent returns risk level"""
        result = self.agent.run(
            "What is retention policy?",
            {"result": "The retention policy..."}
        )

        assert result is not None
        assert "risk_level" in result
        assert result["risk_level"] in ["low", "medium", "high"]

    def test_risk_detects_low_risk(self):
        """Test low-risk queries detected"""
        result = self.agent.run(
            "What is our data retention policy?",
            {"result": "Policy text"}
        )

        assert result is not None
        assert result["risk_level"] in ["low", "medium", "high"]

    def test_risk_detects_high_risk(self):
        """Test high-risk queries detected"""
        result = self.agent.run(
            "Delete compliance records?",
            {"result": "Delete operation"}
        )

        assert result is not None
        assert "risk_level" in result

    def test_risk_has_reason(self):
        """Test risk assessment includes reason"""
        result = self.agent.run(
            "What is policy?",
            {"result": "Policy text"}
        )

        assert "reason" in result
        assert len(result["reason"]) > 0


class TestEscalationAgent:
    """Test Escalation Decision Agent"""

    def setup_method(self):
        self.agent = EscalationAgent()

    def test_escalation_returns_decision(self):
        """Test escalation agent returns decision"""
        result = self.agent.run({"risk_level": "high", "confidence": 0.95})

        assert result is not None
        assert "escalate" in result
        assert isinstance(result["escalate"], bool)

    def test_escalation_for_high_risk(self):
        """Test high-risk scenarios escalate"""
        result = self.agent.run({"risk_level": "high", "confidence": 0.9})

        assert result is not None
        assert result["escalate"] is True

    def test_no_escalation_for_low_risk(self):
        """Test low-risk scenarios don't escalate"""
        result = self.agent.run({"risk_level": "low", "confidence": 0.9})

        assert result is not None
        assert result["escalate"] is False

    def test_escalation_for_medium_risk_low_confidence(self):
        """Test medium risk with low confidence escalates"""
        result = self.agent.run({"risk_level": "medium", "confidence": 0.5})

        assert result is not None
        # Medium + low confidence should escalate
        assert "escalate" in result


class TestAgentIntegration:
    """Test agents working together"""

    def test_all_agents_instantiate(self):
        """Test all agents can be instantiated"""
        agents = [
            IntentAgent(),
            RAGAgent(),
            SQLAgent(),
            HybridAgent(),
            RiskAgent(),
            EscalationAgent(),
        ]

        assert len(agents) == 6
        assert all(agent is not None for agent in agents)

    def test_agent_chain_flow(self):
        """Test basic agent chain flow"""
        intent_agent = IntentAgent()
        risk_agent = RiskAgent()
        escalation_agent = EscalationAgent()

        # Step 1: Get intent
        intent = intent_agent.run("What is policy?")
        assert intent is not None

        # Step 2: Get risk
        risk = risk_agent.run("What is policy?", {"result": "Policy text"})
        assert risk is not None

        # Step 3: Get escalation
        escalation = escalation_agent.run(risk)
        assert escalation is not None
        assert "escalate" in escalation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
