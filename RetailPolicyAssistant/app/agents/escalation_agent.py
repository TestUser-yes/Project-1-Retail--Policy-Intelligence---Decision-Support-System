"""Escalation Agent - Determines if response requires escalation."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
import json


class EscalationAgent(BaseAgent):
    """Determines escalation based on risk level, compliance issues, and business rules."""

    def __init__(self):
        super().__init__(name="escalation_agent", description="Escalation detector")
        # Escalation thresholds and rules
        self.escalation_triggers = {
            "risk_score_threshold": 70,  # Escalate if risk >= 70
            "compliance_failure": True,  # Always escalate on compliance failures
            "high_consequence_keywords": ["delete", "terminate", "legal", "lawsuit", "gdpr", "hipaa", "sox"],
            "vendor_critical_risk": 85,  # Escalate vendors with risk >= 85
        }

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Determine escalation requirements."""
        try:
            # Get data from previous agents
            risk_result = agent_input.previous_outputs.get("risk_result", {})
            compliance_result = agent_input.previous_outputs.get("compliance_result", {})
            query = agent_input.get("query", "").lower()

            # Calculate escalation score
            escalation_score = 0
            escalation_reasons = []

            # Risk-based escalation
            risk_level = risk_result.get("risk_level", "low").lower()
            risk_score = risk_result.get("risk_score", 0)

            if risk_level == "high" or risk_score >= self.escalation_triggers["risk_score_threshold"]:
                escalation_score += 40
                escalation_reasons.append(f"High risk score: {risk_score}")

            elif risk_level == "medium" or risk_score >= 50:
                escalation_score += 20
                escalation_reasons.append(f"Medium risk score: {risk_score}")

            # Compliance-based escalation
            if not compliance_result.get("compliant", True):
                escalation_score += 50
                high_severity = compliance_result.get("severity_high", [])
                escalation_reasons.append(f"Compliance violation: {', '.join(high_severity[:2])}")

            # Keyword-based escalation
            matching_keywords = [kw for kw in self.escalation_triggers["high_consequence_keywords"] if kw in query]
            if matching_keywords:
                escalation_score += 30
                escalation_reasons.append(f"High-consequence keywords detected: {', '.join(matching_keywords)}")

            # Confidence score (inverse relationship with escalation need)
            confidence = min(0.95, (100 - escalation_score) / 100)

            # Determine escalation decision
            escalate = escalation_score >= 50

            return AgentOutput(
                success=True,
                data={
                    "escalate": escalate,
                    "escalation_score": min(100, escalation_score),
                    "confidence": confidence,
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "compliance_compliant": compliance_result.get("compliant", True),
                    "escalation_reasons": escalation_reasons,
                    "escalation_to": "compliance_officer" if escalate else "none",
                    "urgency": "critical" if escalation_score >= 80 else "high" if escalation_score >= 50 else "normal",
                },
                confidence=confidence,
            )

        except Exception as e:
            # On error, default to conservative escalation
            return AgentOutput(
                success=True,
                data={
                    "escalate": True,
                    "escalation_score": 50,
                    "confidence": 0.5,
                    "escalation_reasons": [f"Escalation check error: {str(e)[:50]}"],
                    "escalation_to": "compliance_officer",
                    "urgency": "high",
                },
                confidence=0.5,
            )
