"""
ARCHIVED AGENTS - Planned but Unimplemented

These agent classes were designed as part of the initial agent architecture but have not been
integrated into the active query processing pipeline. They are preserved here for future
implementation or architectural reference.

Status: ARCHIVED (not used in production)
Last Updated: 2026-07-12

Archived Agents:
- IntentAgent (142 lines) - Planned for query intent classification
- RiskAgent (97 lines) - Planned for risk assessment
- RouterAgent (27 lines) - Planned for query routing (now in orchestrator)
- PolicyAgent (18 lines) - Planned for policy reasoning
- ComplianceAgent (109 lines) - Planned for compliance checking
- ValidatorAgent (108 lines) - Planned for response validation
- ConfidenceAgent (31 lines) - Planned for multi-factor confidence scoring
- EscalationAgent (91 lines) - Planned for escalation logic
- ResponseAgent (126 lines) - Planned for response formatting
- ReflectionAgent (145 lines) - Planned for reflection/refinement

ACTIVE AGENTS (in ../agents/):
- RAGAgent - Retrieves policies from vector database
- SQLAgent - Executes semantic SQL queries
- BaseAgent - Base class for all agents

ROADMAP:
These agents could be revived by:
1. Integrating into the orchestrator's agent pipeline
2. Implementing missing business logic
3. Adding them to the LangGraph workflow
4. Creating tests for each agent

For future reference, see:
- app/orchestrator.py - Current query processing pipeline
- app/agents/base_agent.py - Base class and interface
- PROJECT_CLEANUP_REPORT_2026_07_12.md - Cleanup analysis

To restore: move files back to app/agents/ and update __init__.py imports
"""

# Import nothing - these agents are archived and not part of active codebase
__all__ = []
