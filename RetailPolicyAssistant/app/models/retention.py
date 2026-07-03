"""Retention Records Model - Data retention and legal hold tracking."""

from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from datetime import datetime
from app.models.base import Base


class RetentionRecord(Base):
    """Track data retention periods and legal holds."""

    __tablename__ = "retention_records"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String(100), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=True)
    data_category = Column(String(150), nullable=False)
    retention_period_years = Column(Integer, nullable=False)
    legal_hold_flag = Column(Boolean, default=False)
    approval_status = Column(String(50), default="Pending")
    last_review_date = Column(Date, nullable=True)
    next_review_due = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RetentionRecord(department='{self.department}', data_category='{self.data_category}')>"
