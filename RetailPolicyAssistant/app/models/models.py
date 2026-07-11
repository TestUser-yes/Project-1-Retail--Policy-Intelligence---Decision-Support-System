"""SQLAlchemy models for all capstone-required tables."""

from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, Integer, BigInteger, ForeignKey, JSON
from datetime import datetime
from app.models.base import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="viewer")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QueryLog(Base):
    """Logs all queries for auditing."""
    __tablename__ = "query_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    query_text = Column(Text, nullable=False)
    intent = Column(String(50))
    risk_level = Column(String(20))
    response = Column(Text)
    confidence = Column(Float)
    latency_ms = Column(Float)
    escalated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit trail for all actions."""
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)


class ComplianceReview(Base):
    """Compliance review records."""
    __tablename__ = "compliance_reviews"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    query_id = Column(BigInteger, ForeignKey("query_logs.id"))
    reviewer_id = Column(BigInteger, ForeignKey("users.id"))
    compliance_status = Column(String(20))
    notes = Column(Text)
    reviewed_at = Column(DateTime, default=datetime.utcnow)


class RetentionRecord(Base):
    """Data retention records."""
    __tablename__ = "retention_records"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_type = Column(String(100), nullable=False)
    retention_days = Column(Integer)
    deletion_date = Column(DateTime)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)


class Finding(Base):
    """Audit findings."""
    __tablename__ = "findings"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    audit_id = Column(BigInteger)
    severity = Column(String(20))
    description = Column(Text)
    remediation = Column(Text)
    due_date = Column(DateTime)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceMetric(Base):
    """Track compliance metrics."""
    __tablename__ = "compliance_metrics"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float)
    threshold = Column(Float)
    status = Column(String(20))
    measured_at = Column(DateTime, default=datetime.utcnow)


class AgentTrace(Base):
    """Traces for each agent execution."""
    __tablename__ = "agent_traces"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    query_id = Column(BigInteger, ForeignKey("query_logs.id"))
    agent_name = Column(String(100), nullable=False)
    step_number = Column(Integer)
    status = Column(String(20))
    input_data = Column(JSON)
    output_data = Column(JSON)
    duration_ms = Column(Float)
    confidence = Column(Float)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemConfig(Base):
    """System configuration."""
    __tablename__ = "system_config"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
