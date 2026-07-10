from sqlalchemy import Column, Float, Integer, String, Text, TIMESTAMP, func, Boolean

from app.models.base import Base


class AIQuery(Base):
    __tablename__ = "ai_queries"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    result = Column(Text, nullable=True)
    intent = Column(String)
    route = Column(String)
    risk_level = Column(String)
    escalated = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    latency = Column(Float)
    cost_usd = Column(Float, default=0.0)
    created_at = Column(TIMESTAMP, server_default=func.now())
