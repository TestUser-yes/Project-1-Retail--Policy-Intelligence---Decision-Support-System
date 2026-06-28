class EscalationAgent:
    def run(self, risk_result: dict):
        risk = risk_result.get("risk_level", "low")
        return {
            "escalate": risk == "high"
        }
