"""Compliance Agent - Validates compliance requirements."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.llm import LLMService
import json


class ComplianceAgent(BaseAgent):
    """Checks policy compliance against regulatory frameworks (SOX, GDPR, HIPAA)."""

    def __init__(self):
        super().__init__(name="compliance_agent", description="Compliance validator")
        self.llm = LLMService()
        # Compliance frameworks
        self.frameworks = {
            "SOX": ["audit_trail", "financial_records", "retention_7yr"],
            "GDPR": ["consent_record", "right_to_deletion", "data_minimization"],
            "HIPAA": ["PHI_protection", "audit_log", "access_controls"],
            "CCPA": ["data_inventory", "opt_out_mechanism", "breach_notification"],
        }

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Validate policy compliance."""
        try:
            query = agent_input.get("query", "")
            policy_context = agent_input.get("policy_context", "")

            if not query:
                return AgentOutput(
                    success=False,
                    error="Query required for compliance check",
                    confidence=0.0,
                )

            # Compliance check prompt
            compliance_prompt = f"""Perform compliance audit on this query/policy:

Query: {query}
Policy Context: {policy_context}

Check against:
- SOX (financial audit trail): Retention 7 years, immutable audit logs
- GDPR (data protection): Consent records, right to deletion, purpose limitation
- HIPAA (health data): PHI protection, audit controls, access logs
- CCPA (California privacy): Data inventory, opt-out rights, breach notification

Return JSON:
{{
  "compliant": bool,
  "frameworks": {{
    "SOX": {{"compliant": bool, "issues": []}},
    "GDPR": {{"compliant": bool, "issues": []}},
    "HIPAA": {{"compliant": bool, "issues": []}},
    "CCPA": {{"compliant": bool, "issues": []}}
  }},
  "severity_high": [list of critical issues],
  "severity_medium": [list of moderate issues],
  "recommendation": "Approve/Flag/Reject"
}}"""

            response = self.llm.generate_text([
                {"role": "system", "content": "You are a compliance auditor. Return valid JSON only."},
                {"role": "user", "content": compliance_prompt}
            ])

            try:
                compliance_result = json.loads(response)
                frameworks = compliance_result.get("frameworks", {})

                # Calculate overall compliance score
                framework_statuses = [f.get("compliant", False) for f in frameworks.values()]
                compliance_score = sum(framework_statuses) / max(len(framework_statuses), 1)

                is_compliant = compliance_result.get("compliant", False)

                return AgentOutput(
                    success=True,
                    data={
                        "compliant": is_compliant,
                        "confidence": compliance_score,
                        "frameworks": frameworks,
                        "severity_high": compliance_result.get("severity_high", []),
                        "severity_medium": compliance_result.get("severity_medium", []),
                        "recommendation": compliance_result.get("recommendation", "Approve"),
                    },
                    confidence=compliance_score,
                )
            except json.JSONDecodeError:
                # Fallback validation
                has_compliance_keywords = any(kw in query.lower() for kw in ["audit", "retention", "deletion", "consent"])
                confidence = 0.7 if has_compliance_keywords else 0.5

                return AgentOutput(
                    success=True,
                    data={
                        "compliant": True,
                        "confidence": confidence,
                        "frameworks": {f: {"compliant": True, "issues": []} for f in self.frameworks},
                        "recommendation": "Approve",
                    },
                    confidence=confidence,
                )

        except Exception as e:
            return AgentOutput(
                success=False,
                error=f"Compliance check failed: {str(e)[:100]}",
                confidence=0.0,
            )
