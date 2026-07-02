from app.database.session import SessionLocal
from app.models import Vendor


def get_all_vendors():
    db = SessionLocal()
    try:
        vendors = db.query(Vendor).all()
        return [
            {
                "name": v.vendor_name,
                "country": v.country,
                "risk": v.risk_level,
                "status": v.status,
            }
            for v in vendors
        ]
    finally:
        db.close()
