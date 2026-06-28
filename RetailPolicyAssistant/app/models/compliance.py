from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, TIMESTAMP, func

from app.models.base import Base


class ComplianceReview(Base):
    __tablename__ = "compliance_reviews"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    status = Column(String)
    score = Column(Float)
    notes = Column(Text)
    reviewed_at = Column(TIMESTAMP, server_default=func.now())
