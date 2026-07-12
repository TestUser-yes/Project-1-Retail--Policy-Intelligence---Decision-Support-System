"""Risk Agent - Risk classification and escalation detection."""

import re
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.llm import LLMService

llm = LLMService()

# High-risk scenario indicators from README requirements
HIGH_RISK_PATTERNS = {
    "restricted_jurisdiction": [
        r"\b(iran|north korea|syria|cuba|crimea|venezuela|myanmar)\b",
        r"\brestricted jurisdiction",
        r"\bsanctioned country",
        r"\bembargo",
    ],
    "legal_hold_violation": [
        r"\blegal.?hold",
        r"\bactive litigation",
        r"\bdeletion.*legal",
        r"\bdelete.*hold",
        r"\bdelete.*legal",
    ],
    "critical_vendor_approval": [
        r"\bcritical.?risk.*vendor.*approv",
        r"\bnon.?compliant.*approv",
        r"\bapproval override",
        r"\bforce approv",
        r"\bnon-compliant.*approv",
    ],
    "hospitality_violation": [
        r"\bgift.*investigation",
        r"\bhospitality.*investigation",
        r"\bgift.*review",
        r"\bhospitality.*under review",
        r"\bgift.*audit",
    ],
    "overdue_findings": [
        r"\boverdue.*remedi",
        r"\boverdue.*finding",
        r"\boverdue.*audit",
        r"\bfinding.*overdue",
        r"\bopen.*overdue",
    ],
    "conflicting_policies": [
        r"\bconflict.*policy",
        r"\bconflicting.*rule",
        r"\bconflicting.*finding",
        r"\bpolicy conflict",
    ],
    "unresolved_findings": [
        r"\bunresolved.*critical",
        r"\bopen.*critical.*finding",
        r"\bactive.*critical.*issue",
        r"\bcritical.*unresolved",
    ],
    "closure_without_evidence": [
        r"\bclose.*without.*evidence",
        r"\bclose.*high.?severity",
        r"\bclosed.*unresolved",
        r"\bmark.*closed.*evidence",
    ],
    "policy_timeline_violation": [
        r"\bextend.*policy.*timeline",
        r"\bbeyond.*policy.*deadline",
        r"\boverride.*timeline",
    ],
}

# Risk escalation keywords
ESCALATION_KEYWORDS = [
    "override",
    "exception",
    "bypass",
    "waive",
    "approve",
    "reject",
    "delete",
    "remove",
    "escalate",
    "legal",
    "restricted",
    "critical",
    "non-compliant",
]


class RiskAgent(BaseAgent):
    """Risk classification and escalation detection."""

    def __init__(self):
        super().__init__(name="risk_agent", description="Risk classifier")

    def _detect_high_risk_scenarios(self, query: str, result: str) -> tuple[str, list[str]]:
        """Detect specific high-risk scenarios requiring escalation."""
        combined_text = f"{query} {result}".lower()
        detected_scenarios = []
        highest_risk = "low"

        for scenario_type, patterns in HIGH_RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    detected_scenarios.append(scenario_type)
                    highest_risk = "high"
                    break

        return highest_risk, detected_scenarios

    def _calculate_confidence(self, query: str, result: dict) -> float:
        """Calculate confidence score based on result quality."""
        if isinstance(result, dict):
            result_text = str(result.get("result", str(result)))
        else:
            result_text = str(result)

        # Factors that increase confidence
        confidence = 0.5
        if len(result_text) > 100:
            confidence += 0.15
        if "policy" in result_text.lower():
            confidence += 0.1
        if "compliance" in result_text.lower():
            confidence += 0.1
        if re.search(r"\b(approved|denied|required|prohibited)\b", result_text.lower()):
            confidence += 0.1

        # Factors that decrease confidence
        if "uncertain" in result_text.lower() or "unclear" in result_text.lower():
            confidence -= 0.2
        if "conflicting" in result_text.lower():
            confidence -= 0.15
        if len(result_text) < 50:
            confidence -= 0.1

        return min(max(confidence, 0.0), 1.0)

    def _check_policy_violation(self, query: str, result: str) -> bool:
        """Check if the response suggests a policy violation."""
        combined_text = f"{query} {result}".lower()

        violation_indicators = [
            r"\bviolates?\b",
            r"\bnon-compliant",
            r"\bunapproved",
            r"\bnot allowed",
            r"\bnot permitted",
            r"\brestricted",
            r"\bforbidden",
        ]

        for indicator in violation_indicators:
            if re.search(indicator, combined_text):
                return True
        return False

    def _contains_escalation_keywords(self, query: str) -> bool:
        """Check if query contains keywords suggesting high-risk decision."""
        query_lower = query.lower()
        for keyword in ESCALATION_KEYWORDS:
            if keyword in query_lower:
                return True
        return False

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute risk assessment."""
        query = agent_input.query
        result = agent_input.previous_outputs.get("result", {})

        risk_result = self._run_risk_assessment(query, result)

        return AgentOutput(
            success=True,
            data=risk_result,
            confidence=risk_result.get("confidence", 0.0),
        )

    def _run_risk_assessment(self, query: str, result: dict) -> dict:
        """
        Execute risk assessment.

        Returns:
        {
            "risk_level": "low|medium|high",
            "reason": "explanation",
            "confidence": float (0-1),
            "escalation_required": bool,
            "high_risk_scenarios": list,
            "policy_violation": bool
        }
        """
        # Extract result text
        if isinstance(result, dict):
            result_text = str(result.get("result", str(result)))
        else:
            result_text = str(result)

        # Rule-based detections
        pattern_risk, scenarios = self._detect_high_risk_scenarios(query, result_text)
        policy_violation = self._check_policy_violation(query, result_text)
        has_escalation_keywords = self._contains_escalation_keywords(query)
        confidence = self._calculate_confidence(query, result)

        # Determine risk level
        risk_level = "low"
        reason_parts = []

        if pattern_risk == "high" or policy_violation:
            risk_level = "high"
            if scenarios:
                reason_parts.append(f"Detected high-risk scenarios: {', '.join(scenarios)}")
            if policy_violation:
                reason_parts.append("Query may violate compliance policy")

        if has_escalation_keywords and confidence < 0.7:
            risk_level = "medium"
            reason_parts.append("Escalation keywords detected with low confidence")

        if not reason_parts:
            reason_parts.append(f"Standard policy assessment (confidence: {confidence:.0%})")

        reason = "; ".join(reason_parts)

        # Decide escalation
        escalation_required = (
            risk_level == "high" or
            confidence < 0.6 or
            policy_violation or
            len(scenarios) > 0
        )

        return {
            "risk_level": risk_level,
            "reason": reason,
            "confidence": confidence,
            "escalation_required": escalation_required,
            "high_risk_scenarios": scenarios,
            "policy_violation": policy_violation,
        }
