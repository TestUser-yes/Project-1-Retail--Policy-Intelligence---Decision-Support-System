from sqlalchemy import Column, Float, Integer, String, TIMESTAMP, func

from app.models.base import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    risk_score = Column(Float, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
