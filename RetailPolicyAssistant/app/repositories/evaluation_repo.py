from __future__ import annotations

import json

from app.models.evaluation import EvaluationResult, EvaluationRun


class EvaluationRepository:
    def __init__(self, db):
        self.db = db

    def create_run(self, total_tests: int):
        run = EvaluationRun(total_tests=total_tests)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def add_result(self, run_id: int, payload: dict):
        record = EvaluationResult(
            run_id=run_id,
            query=payload["query"],
            expected_route=payload["expected_route"],
            predicted_route=payload["predicted_route"],
            expected_risk=payload["expected_risk"],
            predicted_risk=payload["predicted_risk"],
            expected_escalate=payload["expected_escalate"],
            predicted_escalate=payload["predicted_escalate"],
            expected_answer_contains=json.dumps(payload["expected_answer_contains"], ensure_ascii=True),
            predicted_answer=payload["predicted_answer"],
            passed=payload["passed"],
            reason=payload["reason"],
            latency_seconds=payload["latency_seconds"],
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_run(self, run_id: int, payload: dict):
        run = self.db.get(EvaluationRun, run_id)
        if run is None:
            return None

        run.route_accuracy = payload["route_accuracy"]
        run.answer_accuracy = payload["answer_accuracy"]
        run.risk_accuracy = payload["risk_accuracy"]
        run.escalation_accuracy = payload["escalation_accuracy"]
        run.high_risk_escalation_accuracy = payload["high_risk_escalation_accuracy"]
        run.average_latency = payload["average_latency"]
        run.p95_latency = payload["p95_latency"]
        run.overall_score = payload["overall_score"]
        self.db.commit()
        self.db.refresh(run)

        # TRACE EVALUATION SCORES TO LANGFUSE
        from app.observability.score_tracer import ScoreTracer

        ScoreTracer.log_evaluation_result(
            result_id=str(run_id),
            evaluation_metrics={
                "route_accuracy": payload["route_accuracy"],
                "answer_accuracy": payload["answer_accuracy"],
                "risk_accuracy": payload["risk_accuracy"],
                "escalation_accuracy": payload["escalation_accuracy"],
                "high_risk_escalation_accuracy": payload["high_risk_escalation_accuracy"],
                "overall_score": payload["overall_score"],
                "average_latency_ms": payload["average_latency"],
                "p95_latency_ms": payload["p95_latency"],
            },
            test_name=f"evaluation_run_{run_id}"
        )

        return run

