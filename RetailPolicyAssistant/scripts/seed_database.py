from app.database.session import SessionLocal
from app.models import Vendor


db = SessionLocal()
try:
    db.query(Vendor).delete()
    vendors = [
        Vendor(
            vendor_name="Microsoft",
            country="USA",
            gdpr_compliant=True,
            risk_level="Low",
            status="Approved",
        ),
        Vendor(
            vendor_name="ABC Imports",
            country="China",
            gdpr_compliant=False,
            risk_level="High",
            status="Pending",
        ),
        Vendor(
            vendor_name="Infosys",
            country="India",
            gdpr_compliant=True,
            risk_level="Medium",
            status="Approved",
        ),
    ]
    db.add_all(vendors)
    db.commit()
    print("Seed completed.")
finally:
    db.close()
