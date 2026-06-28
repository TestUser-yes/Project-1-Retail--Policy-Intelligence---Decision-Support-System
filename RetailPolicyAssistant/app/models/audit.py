from sqlalchemy import Column, Integer, JSON, String, TIMESTAMP, func

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    entity = Column(String)
    entity_id = Column(Integer)
    details = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
