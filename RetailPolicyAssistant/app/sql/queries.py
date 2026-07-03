"""SQL Query Handler - Execute safe compliance database queries."""

from app.database.session import SessionLocal
from app.models import Vendor, AuditLog, RetentionRecord, ComplianceReview


def answer_sql(query: str) -> dict:
    """
    Execute a safe SQL query against the compliance database.

    Supports patterns:
    - Vendor queries (status, risk, approval)
    - Audit finding queries (open issues, overdue, severity)
    - Retention queries (legal hold, approval status)
    - Compliance review queries (escalation flags, status)

    Returns:
    {
        "result": str (formatted query results),
        "rows": int (number of results),
        "confidence": float
    }
    """
    db = SessionLocal()
    try:
        query_lower = query.lower()

        # VENDOR QUERIES
        if "vendor" in query_lower and ("critical" in query_lower or "risk" in query_lower):
            vendors = db.query(Vendor).filter(Vendor.risk_category == "Critical").all()
            if vendors:
                result = f"Found {len(vendors)} critical risk vendors:\n"
                result += "\n".join([
                    f"- {v.vendor_name} (Risk: {v.risk_score}, Status: {v.compliance_status})"
                    for v in vendors
                ])
                return {"result": result, "rows": len(vendors), "confidence": 0.95}

        if "vendor" in query_lower and ("non-compliant" in query_lower or "non compliant" in query_lower):
            vendors = db.query(Vendor).filter(Vendor.compliance_status == "Non-Compliant").all()
            if vendors:
                result = f"Found {len(vendors)} non-compliant vendors:\n"
                result += "\n".join([
                    f"- {v.vendor_name} (Risk: {v.risk_category}, Score: {v.risk_score})"
                    for v in vendors
                ])
                return {"result": result, "rows": len(vendors), "confidence": 0.95}

        # AUDIT FINDINGS QUERIES
        if "audit" in query_lower and ("open" in query_lower or "high" in query_lower):
            findings = db.query(AuditLog).filter(
                AuditLog.remediation_status == "Open",
                AuditLog.issue_severity == "High"
            ).all()
            if findings:
                result = f"Found {len(findings)} open high-severity audit findings:\n"
                for f in findings[:5]:
                    vendor = db.query(Vendor).filter(Vendor.vendor_id == f.vendor_id).first()
                    result += f"\n- [{vendor.vendor_name}] {f.issue_title} (Identified: {f.issue_identified_date})"
                return {"result": result, "rows": len(findings), "confidence": 0.95}

        if "audit" in query_lower and "overdue" in query_lower:
            from datetime import datetime
            findings = db.query(AuditLog).filter(
                AuditLog.remediation_status != "Closed",
                AuditLog.target_resolution_date < datetime.now().date()
            ).all()
            if findings:
                result = f"Found {len(findings)} overdue remediation actions:\n"
                for f in findings[:5]:
                    vendor = db.query(Vendor).filter(Vendor.vendor_id == f.vendor_id).first()
                    result += f"\n- [{vendor.vendor_name}] {f.issue_title} (Due: {f.target_resolution_date})"
                return {"result": result, "rows": len(findings), "confidence": 0.95}

        # RETENTION QUERIES
        if "retention" in query_lower and "legal" in query_lower:
            records = db.query(RetentionRecord).filter(RetentionRecord.legal_hold_flag == True).all()
            if records:
                result = f"Found {len(records)} records under legal hold:\n"
                result += "\n".join([
                    f"- {r.data_category} ({r.department}) - Retention: {r.retention_period_years} years"
                    for r in records[:5]
                ])
                return {"result": result, "rows": len(records), "confidence": 0.95}

        # COMPLIANCE REVIEW QUERIES
        if "escalation" in query_lower or "escalate" in query_lower:
            reviews = db.query(ComplianceReview).filter(
                ComplianceReview.review_status.in_(["Open", "In Progress"])
            ).all()
            if reviews:
                result = f"Found {len(reviews)} escalated compliance reviews:\n"
                result += "\n".join([
                    f"- {r.review_type} (Status: {r.review_status}, Reviewer: {r.reviewer_name})"
                    for r in reviews[:5]
                ])
                return {"result": result, "rows": len(reviews), "confidence": 0.95}

        # DEFAULT: Return generic message
        return {
            "result": "Query executed but no specific results found. Please try more specific queries.",
            "rows": 0,
            "confidence": 0.5
        }

    except Exception as e:
        return {
            "result": f"Error executing query: {str(e)}",
            "rows": 0,
            "confidence": 0.0
        }
    finally:
        db.close()
