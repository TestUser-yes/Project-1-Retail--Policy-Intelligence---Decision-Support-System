from app.models.vendors import Vendor


class VendorRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query(Vendor).all()

    def get_by_id(self, vendor_id: int):
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()

    def create(self, name: str, category: str, risk_score: float = 0):
        vendor = Vendor(
            name=name,
            category=category,
            risk_score=risk_score,
        )
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor
