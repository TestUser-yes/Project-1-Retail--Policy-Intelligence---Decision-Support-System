"""Seed sample policies into the database."""

import os
import uuid
from dotenv import load_dotenv

load_dotenv()

from app.database.session import SessionLocal
from app.models.models import PolicyDocument
from app.embeddings import get_embedding

SAMPLE_POLICIES = [
    {
        "title": "Return Policy",
        "content": "Retail return policy: Customers have 30 days to return unused items with original packaging and receipt for a full refund. Items returned after 30 days receive store credit. Clearance items are non-returnable. Used or damaged items must be assessed before refund approval.",
        "category": "Sales & Returns"
    },
    {
        "title": "Refund Policy",
        "content": "Refunds are processed within 5-7 business days after item return approval. Original payment method is refunded. Store credit can be issued immediately. No refunds for items damaged by customer.",
        "category": "Sales & Returns"
    },
    {
        "title": "Employee Discount",
        "content": "Employees receive 15% discount on all items. Management receives 20% discount. Discounts apply to personal purchases only, not gifts. Discount is not combinable with other promotions.",
        "category": "Employee Benefits"
    },
    {
        "title": "Vendor Payment Terms",
        "content": "Standard vendor payment terms: Net 30 days. Early payment discounts: 2% for payment within 10 days. Late payment penalties: 1.5% monthly on overdue amounts. Invoices due by end of month following delivery.",
        "category": "Vendor Management"
    },
    {
        "title": "Pricing Strategy",
        "content": "Product pricing is determined by cost plus 40-50% markup. Sale items can be discounted up to 30%. Clearance items can be discounted up to 70%. Volume discounts available for orders over $5000.",
        "category": "Pricing"
    }
]

if __name__ == "__main__":
    db = SessionLocal()

    try:
        print(f"[INFO] Seeding {len(SAMPLE_POLICIES)} sample policies...")

        for policy_data in SAMPLE_POLICIES:
            # Generate embedding for the policy content
            embedding = get_embedding(policy_data["content"])

            policy = PolicyDocument(
                id=str(uuid.uuid4()),
                title=policy_data["title"],
                content=policy_data["content"],
                category=policy_data["category"],
                embedding=embedding
            )
            db.add(policy)

        db.commit()
        print(f"[SUCCESS] Seeded {len(SAMPLE_POLICIES)} policies with embeddings!")

        # Verify
        count = db.query(PolicyDocument).count()
        print(f"[INFO] Total policies in database: {count}")

    except Exception as e:
        print(f"[ERROR] Failed to seed policies: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
