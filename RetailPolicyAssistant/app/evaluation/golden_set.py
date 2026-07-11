# 50 Golden Test Queries for Retail Policy Intelligence System
# Categories: RAG (15), SQL (10), Hybrid (10), High-Risk (10), Escalation (5)

GOLDEN_SET = [
    # ===== RAG QUERIES (15) - Policy Document Retrieval =====
    {
        "query": "What is our data retention policy for customer records?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["retention", "policy", "data"],
        },
    },
    {
        "query": "How long must we retain email data?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["email", "retention"],
        },
    },
    {
        "query": "What are the GDPR compliance requirements?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["GDPR", "compliance"],
        },
    },
    {
        "query": "What is our vendor approval process?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["vendor", "approval"],
        },
    },
    {
        "query": "What restricted jurisdictions do we have?",
        "expected": {
            "route": "rag",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["jurisdiction", "restricted"],
        },
    },
    {
        "query": "What are our data classification standards?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["classification", "data"],
        },
    },
    {
        "query": "How should we handle PII?",
        "expected": {
            "route": "rag",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["PII", "handle", "personally identifiable"],
        },
    },
    {
        "query": "What is the audit log retention requirement?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["audit", "retention"],
        },
    },
    {
        "query": "Are we compliant with CCPA?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["CCPA", "compliance", "data", "protection"],
            "min_confidence": 0.90,
            "from_pdfs": True,
        },
    },
    {
        "query": "What vendor background check requirements exist?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["vendor", "background", "check"],
        },
    },
    {
        "query": "What is the incident response policy?",
        "expected": {
            "route": "rag",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["incident", "response"],
        },
    },
    {
        "query": "What encryption standards must we follow?",
        "expected": {
            "route": "rag",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["encryption", "standard"],
        },
    },
    {
        "query": "What are the access control requirements?",
        "expected": {
            "route": "rag",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["access", "control"],
        },
    },
    {
        "query": "What is our data breach notification policy?",
        "expected": {
            "route": "rag",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["breach", "notification"],
        },
    },
    {
        "query": "What third-party vendor requirements do we have?",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["vendor", "third-party"],
        },
    },
    # ===== SQL QUERIES (10) - Database Operations =====
    {
        "query": "List all vendors with critical findings",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "critical"],
        },
    },
    {
        "query": "Show me vendors in restricted jurisdictions",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "jurisdiction"],
        },
    },
    {
        "query": "How many vendors have pending approval?",
        "expected": {
            "route": "sql",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["vendor", "pending", "approval"],
        },
    },
    {
        "query": "What is the current compliance status?",
        "expected": {
            "route": "sql",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["compliance", "status"],
        },
    },
    {
        "query": "List all rejected vendors",
        "expected": {
            "route": "sql",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["vendor", "rejected"],
        },
    },
    {
        "query": "How many policy documents do we have?",
        "expected": {
            "route": "sql",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["policy", "documents", "count"],
        },
    },
    {
        "query": "Show recent audit log entries",
        "expected": {
            "route": "sql",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["audit", "recent"],
        },
    },
    {
        "query": "List all high-risk retention records",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["retention", "high-risk"],
        },
    },
    {
        "query": "What vendor retention policies exist?",
        "expected": {
            "route": "sql",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["vendor", "retention"],
        },
    },
    {
        "query": "How many queries have been escalated?",
        "expected": {
            "route": "sql",
            "risk": "low",
            "escalate": False,
            "answer_contains": ["escalated", "query", "count"],
        },
    },
    # ===== HYBRID QUERIES (10) - Policy + Database =====
    {
        "query": "Is vendor 456 compliant with our retention policy?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "retention", "compliant"],
        },
    },
    {
        "query": "What compliance issues does vendor 789 have?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "compliance"],
        },
    },
    {
        "query": "Are restricted jurisdiction vendors following our policy?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["jurisdiction", "vendor", "policy"],
        },
    },
    {
        "query": "Which vendors fail our encryption standards?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "encryption", "fail"],
        },
    },
    {
        "query": "Do we have vendors with unresolved critical findings?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "critical"],
        },
    },
    {
        "query": "How does vendor 123 align with GDPR requirements?",
        "expected": {
            "route": "hybrid",
            "risk": "medium",
            "escalate": False,
            "answer_contains": ["vendor", "GDPR"],
        },
    },
    {
        "query": "Show vendors with pending approvals and policy gaps",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "pending", "policy"],
        },
    },
    {
        "query": "Which vendors need access control updates?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "access", "control"],
        },
    },
    {
        "query": "List vendors with both retention and compliance issues",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "retention", "compliance"],
        },
    },
    {
        "query": "Are all critical-finding vendors following incident response policy?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "critical", "incident"],
        },
    },
    # ===== HIGH-RISK QUERIES (10) - Should detect risk patterns =====
    {
        "query": "Override vendor approval for vendor 456 despite critical findings?",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["approval", "override"],
        },
    },
    {
        "query": "Delete compliance records for audit purposes?",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["delete", "compliance"],
        },
    },
    {
        "query": "Can we bypass encryption requirements for performance?",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["encryption", "bypass"],
        },
    },
    {
        "query": "Should we disable data retention for legacy systems?",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["retention", "disable"],
        },
    },
    {
        "query": "Is it acceptable to store PII in logs?",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["PII", "logs"],
        },
    },
    {
        "query": "Can we approve vendor in restricted jurisdiction?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "jurisdiction"],
        },
    },
    {
        "query": "Override audit logging to improve performance?",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["audit", "override"],
        },
    },
    {
        "query": "Can we reduce GDPR compliance scope for cost savings?",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["GDPR", "scope"],
        },
    },
    {
        "query": "Should we store unencrypted sensitive data temporarily?",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["encryption", "sensitive"],
        },
    },
    {
        "query": "Can we disable access controls during migration?",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["access", "control"],
        },
    },
    # ===== ESCALATION QUERIES (5) - Must escalate =====
    {
        "query": "Approve vendor with critical findings and restricted jurisdiction",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["vendor", "critical"],
        },
    },
    {
        "query": "Delete compliance audit logs for all critical vendors",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["delete", "audit"],
        },
    },
    {
        "query": "Override encryption policy for data center migration",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["encryption", "override"],
        },
    },
    {
        "query": "Disable PII protection during system upgrade",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["PII", "protection"],
        },
    },
    {
        "query": "Reduce retention requirements to recover storage space",
        "expected": {
            "route": "rag",
            "risk": "high",
            "escalate": True,
            "answer_contains": ["retention", "reduce"],
        },
    },
]
