from __future__ import annotations

import json
from datetime import datetime, timezone

from app.database.session import SessionLocal
from app.evaluation.answer_metric import AnswerMetric
from app.evaluation.escalation_metric import EscalationMetric
from app.evaluation.golden_set import GOLDEN_SET
from app.evaluation.latency_metric import LatencyMetric
from app.evaluation.route_metric import RouteMetric
from app.evaluation.risk_metric import RiskMetric
from app.evaluation.slos import (
    ANSWER_ACCURACY_TARGET,
    AVERAGE_LATENCY_TARGET_SECONDS,
    ESCALATION_ACCURACY_TARGET,
    P95_LATENCY_TARGET_SECONDS,
    RISK_ACCURACY_TARGET,
    ROUTE_ACCURACY_TARGET,
)
from app.orchestrator import Orchestrator
from app.repositories.evaluation_repo import EvaluationRepository
from app.evaluation.utils import normalize_text


class Evaluator:
    def __init__(self):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)
        self.repository = EvaluationRepository(self.db)
        self.route_metric = RouteMetric()
        self.answer_metric = AnswerMetric()
        self.risk_metric = RiskMetric()
        self.escalation_metric = EscalationMetric()
        self.latency_metric = LatencyMetric()

    def _extract_response(self, response: dict):
        route = normalize_text(response.get("route", "unknown")).strip().lower()
        risk_block = response.get("risk", {})
        if isinstance(risk_block, dict):
            risk_level = normalize_text(risk_block.get("risk_level", "unknown")).strip().lower()
        else:
            risk_level = normalize_text(risk_block).strip().lower()

        escalate = response.get("escalate", False)
        latency = float(response.get("latency", response.get("latency_seconds", 0.0)) or 0.0)

        result_block = response.get("result", {})
        if isinstance(result_block, dict):
            predicted_answer = result_block.get("result", result_block.get("answer", result_block))
        else:
            predicted_answer = result_block

        if isinstance(predicted_answer, (dict, list)):
            predicted_answer_text = json.dumps(predicted_answer, ensure_ascii=True)
        else:
            predicted_answer_text = normalize_text(predicted_answer)

        return route, risk_level, escalate, latency, predicted_answer_text

    def _build_reason(self, checks: list[str]):
        failures = [reason for reason in checks if reason]
        return "; ".join(failures)

    def run(self):
        results = []

        try:
            run = self.repository.create_run(total_tests=len(GOLDEN_SET))

            for item in GOLDEN_SET:
                expected = item["expected"]
                try:
                    response = self.orchestrator.run(item["query"])

                    if "error" in response:
                        raise RuntimeError(response.get("details", response["error"]))

                    predicted_route, predicted_risk, predicted_escalate, latency, predicted_answer = self._extract_response(response)

                    route_result = self.route_metric.evaluate(expected["route"], predicted_route)
                    answer_result = self.answer_metric.evaluate(expected.get("answer_contains", []), predicted_answer)
                    risk_result = self.risk_metric.evaluate(expected["risk"], predicted_risk)
                    escalation_result = self.escalation_metric.evaluate(
                        expected["escalate"],
                        predicted_escalate,
                        risk_level=expected["risk"],
                    )
                    self.latency_metric.record(latency)

                    passed = all(
                        [
                            route_result["passed"],
                            answer_result["passed"],
                            risk_result["passed"],
                            escalation_result["passed"],
                        ]
                    )
                    reason = self._build_reason(
                        [
                            route_result["reason"],
                            answer_result["reason"],
                            risk_result["reason"],
                            escalation_result["reason"],
                        ]
                    )
                except Exception as exc:
                    predicted_route = "error"
                    predicted_risk = "error"
                    predicted_escalate = False
                    predicted_answer = ""
                    latency = 0.0
                    passed = False
                    reason = f"Evaluation error: {exc}"
                    self.latency_metric.record(latency)

                result_payload = {
                    "query": item["query"],
                    "expected_route": expected["route"],
                    "predicted_route": predicted_route,
                    "expected_risk": expected["risk"],
                    "predicted_risk": predicted_risk,
                    "expected_escalate": expected["escalate"],
                    "predicted_escalate": predicted_escalate,
                    "expected_answer_contains": expected.get("answer_contains", []),
                    "predicted_answer": predicted_answer,
                    "passed": passed,
                    "reason": reason,
                    "latency_seconds": latency,
                }
                self.repository.add_result(run.id, result_payload)
                results.append(result_payload)

            route_accuracy = self.route_metric.score()
            answer_accuracy = self.answer_metric.score()
            risk_accuracy = self.risk_metric.score()
            escalation_accuracy = self.escalation_metric.score()
            high_risk_escalation_accuracy = self.escalation_metric.high_risk_score()
            average_latency = self.latency_metric.average()
            p95_latency = self.latency_metric.p95()
            overall_score = (
                route_accuracy
                + answer_accuracy
                + risk_accuracy
                + escalation_accuracy
            ) / 4

            summary = {
                "total_tests": len(GOLDEN_SET),
                "route_accuracy": route_accuracy,
                "answer_accuracy": answer_accuracy,
                "risk_accuracy": risk_accuracy,
                "escalation_accuracy": escalation_accuracy,
                "high_risk_escalation_accuracy": high_risk_escalation_accuracy,
                "average_latency": average_latency,
                "p95_latency": p95_latency,
                "overall_score": overall_score,
                "slo_targets": {
                    "route_accuracy": ROUTE_ACCURACY_TARGET,
                    "answer_accuracy": ANSWER_ACCURACY_TARGET,
                    "risk_accuracy": RISK_ACCURACY_TARGET,
                    "escalation_accuracy": ESCALATION_ACCURACY_TARGET,
                    "average_latency": AVERAGE_LATENCY_TARGET_SECONDS,
                    "p95_latency": P95_LATENCY_TARGET_SECONDS,
                },
                "slo_status": {
                    "route_accuracy": route_accuracy >= ROUTE_ACCURACY_TARGET,
                    "answer_accuracy": answer_accuracy >= ANSWER_ACCURACY_TARGET,
                    "risk_accuracy": risk_accuracy >= RISK_ACCURACY_TARGET,
                    "escalation_accuracy": high_risk_escalation_accuracy >= ESCALATION_ACCURACY_TARGET,
                    "average_latency": average_latency <= AVERAGE_LATENCY_TARGET_SECONDS,
                    "p95_latency": p95_latency <= P95_LATENCY_TARGET_SECONDS,
                },
            }

            self.repository.update_run(run.id, summary)

            failed_cases = [result for result in results if not result["passed"]]

            return {
                "run_id": run.id,
                "run_time": run.run_time if run.run_time else datetime.now(timezone.utc),
                "summary": summary,
                "results": results,
                "failed_cases": failed_cases,
            }
        finally:
            self.db.close()
