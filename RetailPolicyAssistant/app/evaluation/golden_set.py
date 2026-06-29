GOLDEN_SET = [
    {
        "id": 1,
        "query": "What is the vendor compliance status of Vendor A?",
        "expected": {
            "route": "sql",
            "risk": "low",
            "escalate": False,
            "answer_contains": [
                "Vendor A",
                "compliance",
            ],
        },
    },
    {
        "id": 2,
        "query": "Summarize the return policy for electronics",
        "expected": {
            "route": "rag",
            "risk": "low",
            "escalate": False,
            "answer_contains": [
                "electronics",
                "return",
                "policy",
            ],
        },
    },
    {
        "id": 3,
        "query": "Compare vendor compliance with policy violations and summarize risk",
        "expected": {
            "route": "hybrid",
            "risk": "medium",
            "escalate": False,
            "answer_contains": [
                "vendor",
                "policy",
                "risk",
            ],
        },
    },
    {
        "id": 4,
        "query": "Can we approve a vendor with missing compliance documents?",
        "expected": {
            "route": "hybrid",
            "risk": "high",
            "escalate": True,
            "answer_contains": [
                "missing compliance documents",
                "vendor",
                "approval",
            ],
        },
    },
    {
        "id": 5,
        "query": "List all vendors with risk score above 0.8",
        "expected": {
            "route": "sql",
            "risk": "high",
            "escalate": True,
            "answer_contains": [
                "Vendor",
                "0.8",
            ],
        },
    },
]
