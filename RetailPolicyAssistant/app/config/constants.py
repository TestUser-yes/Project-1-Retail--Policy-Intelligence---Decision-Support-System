"""
System-wide constants and configuration values.
These should not be hardcoded in multiple files.
"""

from typing import Dict, List

# ==================== SLO & Performance Targets ====================
SLO_TARGETS = {
    "task_success_rate": 0.90,  # 90% TSR from capstone spec
    "p95_latency_seconds": 3.0,  # 3-6 seconds from capstone spec
    "latency_seconds": 2.0,  # Default target
    "route_accuracy": 0.95,  # 95% correctness
    "answer_accuracy": 0.90,  # 90% answer quality
    "risk_accuracy": 0.95,  # 95% risk classification
    "escalation_accuracy": 1.00,  # 100% escalation detection
}

# ==================== SLO ENFORCEMENT CONFIGURATION ====================
SLO_ENFORCEMENT = {
    "enforce_latency": True,  # Enforce latency SLO boundaries
    "enforce_confidence": True,  # Enforce confidence score minimum
    "enforce_accuracy": True,  # Enforce accuracy SLO
    "latency_target_ms": 2000,  # Target latency (ms)
    "latency_hard_limit_ms": 2400,  # Hard limit for rejection (ms)
    "confidence_min": 0.70,  # Minimum confidence (70%)
}

# ==================== BUDGET CONFIGURATION ====================
BUDGET_CONFIG = {
    "daily_limit_usd": 100.0,  # $100/day limit
    "monthly_limit_usd": 2000.0,  # $2000/month limit
    "alert_threshold": 0.80,  # Alert at 80% usage
    "stop_threshold": 0.95,  # Stop processing at 95% usage
}

# ==================== QUERY CONSTRAINTS ====================
QUERY_CONSTRAINTS = {
    "min_length": 3,  # Minimum 3 characters
    "max_length": 10000,  # Maximum 10,000 characters
}

# ==================== RESPONSE CONSTRAINTS ====================
RESPONSE_CONSTRAINTS = {
    "max_length": 100000,  # Maximum 100K characters
}

# ==================== CACHE CONFIGURATION ====================
CACHE_CONFIG = {
    "query_cache_size": 1000,  # Max 1000 cached queries
    "query_ttl_seconds": 3600,  # 1 hour TTL
    "embedding_cache_size": 10000,  # Max 10K embeddings
}

# ==================== RATE LIMITING ====================
RATE_LIMITS = {
    "user_requests_per_hour": 100,  # 100 requests/hour per user
    "global_requests_per_hour": 1000,  # 1000 requests/hour globally
}

# ==================== MEMORY MANAGEMENT ====================
MEMORY_CONFIG = {
    "max_messages_per_conversation": 100,  # Max 100 messages
    "conversation_timeout_hours": 24,  # 24-hour timeout
}

# ==================== LOGGING ====================
LOGGING_CONFIG = {
    "max_file_size_bytes": 10 * 1024 * 1024,  # 10 MB per log file
    "backup_count": 5,  # Keep 5 backup files
}

# ==================== DATASET - RETAIL POLICY INTELLIGENCE ====================
# As per capstone_retail_policy_intelligence_dataset.md

# Database name
DATABASE_NAME = "retail_compliance_db"

# Table schema definitions (for reference)
TABLES = {
    "vendors": {
        "columns": [
            "vendor_id", "vendor_name", "risk_score", "risk_category",
            "compliance_status", "approval_status", "onboarding_date",
            "last_audit_date", "next_review_due", "created_at"
        ],
        "required_for": ["vendor compliance queries", "risk assessment"]
    },
    "audit_logs": {
        "columns": [
            "audit_id", "vendor_id", "policy_reference", "issue_title",
            "issue_severity", "remediation_status", "issue_identified_date",
            "target_resolution_date", "resolution_date", "escalation_flag", "created_at"
        ],
        "required_for": ["audit findings", "escalation detection"]
    },
    "retention_records": {
        "columns": [
            "retention_id", "department", "vendor_id", "data_category",
            "retention_period_years", "legal_hold_flag", "approval_status",
            "last_review_date", "next_review_due", "created_at"
        ],
        "required_for": ["retention policy queries", "data protection"]
    },
    "compliance_reviews": {
        "columns": [
            "review_id", "vendor_id", "reviewer_name", "review_type",
            "review_status", "review_notes", "review_date", "next_review_due", "created_at"
        ],
        "required_for": ["compliance tracking", "review status"]
    }
}

# ==================== QUERY ROUTING ====================
# As per README.md requirements
QUERY_ROUTING = {
    "RAG": {
        "description": "Policy explanation, clause interpretation, summaries",
        "triggers": [
            "retention rules", "policy requirements", "what are",
            "explain", "interpret", "summarize", "describe"
        ]
    },
    "SQL": {
        "description": "Compliance records, approval status, audit logs",
        "triggers": [
            "list vendors", "count", "show", "find", "vendors with",
            "compliance records", "audit findings"
        ]
    },
    "HYBRID": {
        "description": "Interpretation + structured validation",
        "triggers": [
            "comply with", "aligned with", "require suspension",
            "policy compliance", "legal compliance"
        ]
    },
    "MULTI_AGENT": {
        "description": "High-risk validation workflows",
        "high_risk_indicators": [
            "override", "suspension", "deletion", "legal hold",
            "critical risk", "escalation", "non-compliant"
        ]
    }
}

# ==================== RISK LEVELS ====================
# As per capstone requirements
RISK_LEVELS = {
    "LOW": "Routine policy query",
    "MEDIUM": "Query involves approval/compliance review",
    "HIGH": "Query flagged for potential compliance risk or out-of-scope"
}

# ==================== ESCALATION TRIGGERS ====================
# Mandatory escalation scenarios from capstone_retail_policy_intelligence_dataset.md
ESCALATION_TRIGGERS = {
    "cross_border_data_transfer": "Cross-border data transfer involving restricted jurisdictions",
    "legal_hold_deletion": "Deletion request for records under active legal hold",
    "critical_risk_override": "Approval override for a Critical-risk vendor",
    "hospitality_overseas": "Hospitality or gift approval involving overseas suppliers",
    "overdue_audit": "Audit findings overdue beyond target resolution date",
    "conflicting_policies": "Conflicting policy clauses across departments",
    "vendor_onboarding_findings": "Vendor onboarding with unresolved compliance findings",
    "closed_without_resolution": "High-severity issue marked 'Closed' without resolution evidence",
    "low_confidence": "Confidence score below threshold",
}

# ==================== POLICY DOCUMENTS ====================
# As per capstone requirements - unstructured RAG data
POLICY_DOCUMENTS = [
    "Retail Data Protection & Customer Privacy Policy",
    "Data Retention & Archival Policy",
    "Supplier & Vendor Compliance Policy",
    "Anti-Bribery & Ethical Conduct Policy",
    "Information Security & Access Control Policy",
    "GDPR Selected Articles (Excerpt)",
    "ISO 27001 Access Control Summary"
]

# ==================== QUERY DISTRIBUTION ====================
# As per capstone requirements - 50 golden queries distribution
QUERY_DISTRIBUTION = {
    "policy_interpretation_rag": 15,
    "structured_lookup_sql": 10,
    "hybrid_reasoning": 10,
    "high_risk_regulatory": 10,
    "escalation_scenarios": 5,
    "total": 50
}

# ==================== COMPLIANCE STATUSES ====================
COMPLIANCE_STATUSES = [
    "Compliant",
    "Under Review",
    "Non-Compliant"
]

# ==================== APPROVAL STATUSES ====================
APPROVAL_STATUSES = [
    "Approved",
    "Pending",
    "Rejected"
]

# ==================== RISK CATEGORIES ====================
RISK_CATEGORIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

# ==================== REMEDIATION STATUSES ====================
REMEDIATION_STATUSES = [
    "Open",
    "In Progress",
    "Closed"
]

# ==================== REVIEW STATUSES ====================
REVIEW_STATUSES = [
    "Open",
    "In Progress",
    "Closed"
]

# ==================== ISSUE SEVERITY ====================
ISSUE_SEVERITY_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

# ==================== HELPER FUNCTIONS ====================

def get_slo_target(metric: str) -> float:
    """Get SLO target for a specific metric."""
    return SLO_TARGETS.get(metric, 0.0)


def get_query_max_length() -> int:
    """Get maximum allowed query length."""
    return QUERY_CONSTRAINTS.get("max_length", 10000)


def get_budget_daily_limit() -> float:
    """Get daily budget limit in USD."""
    return BUDGET_CONFIG.get("daily_limit_usd", 100.0)


def is_high_risk_escalation_trigger(query_text: str) -> bool:
    """Check if query contains high-risk escalation triggers."""
    query_lower = query_text.lower()
    for trigger_key, trigger_text in ESCALATION_TRIGGERS.items():
        if any(word in query_lower for word in trigger_text.lower().split()):
            return True
    return False


def get_expected_route_for_query(query_text: str) -> str:
    """Predict expected route for a query based on keywords."""
    query_lower = query_text.lower()

    # Check for multi-agent triggers first
    for trigger in QUERY_ROUTING["MULTI_AGENT"]["high_risk_indicators"]:
        if trigger in query_lower:
            return "MULTI_AGENT"

    # Check for hybrid triggers
    for trigger in QUERY_ROUTING["HYBRID"]["triggers"]:
        if trigger in query_lower:
            return "HYBRID"

    # Check for SQL triggers
    for trigger in QUERY_ROUTING["SQL"]["triggers"]:
        if trigger in query_lower:
            return "SQL"

    # Check for RAG triggers
    for trigger in QUERY_ROUTING["RAG"]["triggers"]:
        if trigger in query_lower:
            return "RAG"

    # Default to RAG for policy queries
    return "RAG"
