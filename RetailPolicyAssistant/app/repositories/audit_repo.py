from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, db):
        self.db = db

    def log(self, action: str, entity: str, entity_id: int, metadata: dict):
        record = AuditLog(
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=metadata,
        )
        self.db.add(record)
        self.db.commit()
        return record
