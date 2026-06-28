from app.models.compliance import ComplianceReview


class ComplianceRepository:
    def __init__(self, db):
        self.db = db

    def get_by_vendor(self, vendor_id: int):
        return (
            self.db.query(ComplianceReview)
            .filter(ComplianceReview.vendor_id == vendor_id)
            .all()
        )

    def create(self, vendor_id: int, status: str, score: float, notes: str):
        record = ComplianceReview(
            vendor_id=vendor_id,
            status=status,
            score=score,
            notes=notes,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
