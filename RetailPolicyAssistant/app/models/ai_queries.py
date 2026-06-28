from sqlalchemy import Column, Float, Integer, String, Text, TIMESTAMP, func

from app.models.base import Base


class AIQuery(Base):
    __tablename__ = "ai_queries"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    intent = Column(String)
    route = Column(String)
    risk_level = Column(String)
    latency = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())
