from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text

from app.models.base import Base


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)

    # New metadata
    document_name = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    section = Column(String(255), nullable=True)

    # Chunk text
    content = Column(Text, nullable=False)

    # OpenAI embedding
    embedding = Column(Vector(1536))
