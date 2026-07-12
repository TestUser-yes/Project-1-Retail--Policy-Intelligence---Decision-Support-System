from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_time = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    total_tests = Column(Integer, nullable=False, default=0)
    route_accuracy = Column(Float, nullable=False, default=0.0)
    answer_accuracy = Column(Float, nullable=False, default=0.0)
    risk_accuracy = Column(Float, nullable=False, default=0.0)
    escalation_accuracy = Column(Float, nullable=False, default=0.0)
    high_risk_escalation_accuracy = Column(Float, nullable=False, default=0.0)
    average_latency = Column(Float, nullable=False, default=0.0)
    p95_latency = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0)

    results = relationship("EvaluationResult", back_populates="run", cascade="all, delete-orphan")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("evaluation_runs.id"), index=True, nullable=False)
    query = Column(Text, nullable=False)
    expected_route = Column(String, nullable=False)
    predicted_route = Column(String, nullable=False)
    expected_risk = Column(String, nullable=False)
    predicted_risk = Column(String, nullable=False)
    expected_escalate = Column(Boolean, nullable=False)
    predicted_escalate = Column(Boolean, nullable=False)
    expected_answer_contains = Column(Text, nullable=False)
    predicted_answer = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False, default=False)
    reason = Column(Text, nullable=False, default="")
    latency_seconds = Column(Float, nullable=False, default=0.0)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    run = relationship("EvaluationRun", back_populates="results")


class Phase2Run(Base):
    """Phase 2 retrieval quality evaluation run."""

    __tablename__ = "phase2_evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_time = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    total_evals = Column(Integer, nullable=False, default=0)
    avg_context_precision = Column(Float, nullable=False, default=0.0)
    avg_context_recall = Column(Float, nullable=False, default=0.0)
    avg_retrieval_latency_ms = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0)

    results = relationship("Phase2Result", back_populates="run", cascade="all, delete-orphan")


class Phase2Result(Base):
    """Individual Phase 2 retrieval evaluation result."""

    __tablename__ = "phase2_evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("phase2_evaluation_runs.id"), index=True, nullable=False)
    query = Column(Text, nullable=False)
    context_precision = Column(Float, nullable=False, default=0.0)
    context_recall = Column(Float, nullable=False, default=0.0)
    retrieved_doc_count = Column(Integer, nullable=False, default=0)
    retrieval_method = Column(String, nullable=False, default="unknown")
    route = Column(String, nullable=False, default="rag")
    retrieval_latency_ms = Column(Float, nullable=False, default=0.0)
    avg_chunk_relevance = Column(Float, nullable=False, default=0.0)
    retrieval_diversity_score = Column(Float, nullable=False, default=0.0)
    precision_status = Column(String, nullable=False, default="good")
    recall_status = Column(String, nullable=False, default="good")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    run = relationship("Phase2Run", back_populates="results")
