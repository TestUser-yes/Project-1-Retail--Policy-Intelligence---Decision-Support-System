from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String, nullable=False)
    country = Column(String)
    gdpr_compliant = Column(Boolean, default=False)
    risk_level = Column(String)
    status = Column(String)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String)
    department = Column(String)
    manager = Column(String)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event = Column(String)
    severity = Column(String)
    created_at = Column(Date)


class PolicyAcknowledgement(Base):
    __tablename__ = "policy_acknowledgements"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    policy_name = Column(String)
    acknowledged = Column(Boolean, default=False)

    employee = relationship("Employee")


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    description = Column(String)
    status = Column(String)

    vendor = relationship("Vendor")
