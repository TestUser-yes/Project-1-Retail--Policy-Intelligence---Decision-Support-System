"""
ARCHIVED MODULES - Planned but Unimplemented

These modules were designed for future functionality but have not been integrated
into the active query processing pipeline. They are preserved here for future
implementation or architectural reference.

Status: ARCHIVED (not used in production)
Last Updated: 2026-07-12

Archived Modules:

1. **LangGraph Workflow** (2 files)
   - langgraph_workflow.py - Placeholder for 11-step LangGraph orchestration
   - state.py - Workflow state definition
   - Status: Incomplete (has build_graph() TODO)
   - Current: Query processing uses Orchestrator class directly
   - Future: Could implement full LangGraph integration for complex workflows

CURRENT ARCHITECTURE:
- Orchestrator (app/orchestrator.py) - Direct query processing
- Agents (app/agents/) - RAGAgent and SQLAgent only
- Pipeline (app/rag/, app/sql/) - Direct retrieval and query execution

ROADMAP:
These modules could be revived by:
1. Implementing the full LangGraph graph construction
2. Integrating all 11 workflow steps into LangGraph state machine
3. Connecting archived agents to the workflow nodes
4. Adding proper state transitions and error handling

For future reference, see:
- app/orchestrator.py - Current query processing pipeline
- PROJECT_CLEANUP_REPORT_2026_07_12.md - Cleanup analysis
- PHASE 2 cleanup report - Additional context

To restore: Move files back to app/workflow/ and implement missing functionality
"""

__all__ = []
