from __future__ import annotations

import json

from app.models.evaluation import EvaluationResult, EvaluationRun, Phase2Run, Phase2Result


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

    # ===== PHASE 2: RETRIEVAL QUALITY METRICS =====

    def create_phase2_run(self, total_evals: int = 0):
        """Create a new Phase 2 evaluation run.

        Args:
            total_evals: Number of evaluations in this run

        Returns:
            Phase2Run instance
        """
        run = Phase2Run(total_evals=total_evals)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def add_phase2_result(self, run_id: int, payload: dict):
        """Add a Phase 2 evaluation result.

        Args:
            run_id: ID of the Phase 2 evaluation run
            payload: Dictionary with retrieval metrics

        Returns:
            Phase2Result instance
        """
        record = Phase2Result(
            run_id=run_id,
            query=payload.get("query", ""),
            context_precision=payload.get("context_precision", 0.0),
            context_recall=payload.get("context_recall", 0.0),
            retrieved_doc_count=payload.get("retrieved_doc_count", 0),
            retrieval_method=payload.get("retrieval_method", "unknown"),
            route=payload.get("route", "rag"),
            retrieval_latency_ms=payload.get("retrieval_latency_ms", 0.0),
            avg_chunk_relevance=payload.get("avg_chunk_relevance", 0.0),
            retrieval_diversity_score=payload.get("retrieval_diversity_score", 0.0),
            precision_status=payload.get("precision_status", "good"),
            recall_status=payload.get("recall_status", "good"),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_phase2_run(self, run_id: int, payload: dict):
        """Update Phase 2 evaluation run aggregates.

        Args:
            run_id: ID of the Phase 2 run
            payload: Dictionary with aggregate metrics

        Returns:
            Updated Phase2Run instance
        """
        run = self.db.get(Phase2Run, run_id)
        if run is None:
            return None

        run.total_evals = payload.get("total_evals", run.total_evals)
        run.avg_context_precision = payload.get("avg_context_precision", 0.0)
        run.avg_context_recall = payload.get("avg_context_recall", 0.0)
        run.avg_retrieval_latency_ms = payload.get("avg_retrieval_latency_ms", 0.0)
        run.overall_score = payload.get("overall_score", 0.0)
        self.db.commit()
        self.db.refresh(run)

        # Log to Langfuse
        from app.observability.score_tracer import ScoreTracer

        ScoreTracer.log_score(
            score_name="phase2_run_metrics",
            score_value=run.overall_score,
            metadata={
                "run_id": str(run_id),
                "avg_context_precision": run.avg_context_precision,
                "avg_context_recall": run.avg_context_recall,
                "total_evals": run.total_evals,
                "avg_retrieval_latency_ms": run.avg_retrieval_latency_ms,
            }
        )

        return run

