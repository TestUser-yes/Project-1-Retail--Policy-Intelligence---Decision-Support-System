from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text, TIMESTAMP, func

from app.models.base import Base


class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("ai_queries.id"))
    response = Column(Text)
    escalate = Column(Boolean)
    created_at = Column(TIMESTAMP, server_default=func.now())
