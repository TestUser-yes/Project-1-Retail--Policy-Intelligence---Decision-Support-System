from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from pgvector.sqlalchemy import Vector

from app.models.base import Base


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    embedding = Column(Vector(1536))
    created_at = Column(TIMESTAMP, server_default=func.now())
