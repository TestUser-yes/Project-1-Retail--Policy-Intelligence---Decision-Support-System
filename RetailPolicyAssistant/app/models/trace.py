from sqlalchemy import Column, Integer, JSON, Text, TIMESTAMP, func

from app.models.base import Base


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    stage = Column(Text)
    data = Column(JSON)
    timestamp = Column(TIMESTAMP, server_default=func.now())
