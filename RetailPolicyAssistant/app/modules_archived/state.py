"""Workflow State - Shared state across all agents."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowState:
    """Immutable workflow state object."""
    
    query: str
    user_id: str = "anonymous"
    
    # Intent Detection
    intent: Optional[str] = None
    
    # Risk Assessment
    risk_level: Optional[str] = None
    risk_scenarios: List[str] = field(default_factory=list)
    
    # Routing Decision
    route: Optional[str] = None
    
    # Retrieval Results
    rag_documents: List[Dict] = field(default_factory=list)
    rag_confidence: float = 0.0
    
    # SQL Results
    sql_result: Optional[Any] = None
    sql_confidence: float = 0.0
    
    # Policy Results
    policy_answer: Optional[str] = None
    policy_confidence: float = 0.0
    
    # Compliance Check
    is_compliant: bool = True
    
    # Validation
    is_valid: bool = True
    
    # Reflection
    reflection_confidence: float = 0.0
    
    # Final Confidence
    final_confidence: float = 0.0
    
    # Escalation
    requires_escalation: bool = False
    
    # Final Response
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Traces
    traces: List[Dict] = field(default_factory=list)
