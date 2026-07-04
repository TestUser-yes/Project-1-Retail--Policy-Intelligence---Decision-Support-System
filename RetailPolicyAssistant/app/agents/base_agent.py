"""
Base Agent Class - Foundation for all 11 specialized agents.

Each agent inherits from BaseAgent and implements a single responsibility.
Agents operate within LangGraph workflow and maintain consistent interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class AgentTrace:
    """Trace information for a single agent execution."""
    agent_name: str
    step_number: int
    status: AgentStatus
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInput:
    """Standard input structure for all agents."""
    query: str
    context: Dict[str, Any] = field(default_factory=dict)
    previous_outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    """Standard output structure for all agents."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    confidence: float = 1.0  # 0-1 confidence score
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all 11 specialized agents.

    Each agent:
    - Has a single responsibility
    - Operates asynchronously
    - Maintains trace information
    - Reports confidence in output
    - Handles errors gracefully
    """

    def __init__(
        self,
        name: str,
        description: str,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.7,
    ):
        """
        Initialize base agent.

        Args:
            name: Agent identifier (e.g., 'intent_agent')
            description: What this agent does
            model: LLM model to use
            temperature: LLM temperature (0-1)
        """
        self.name = name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(f"agent.{name}")
        self.traces: List[AgentTrace] = []

    async def run(self, agent_input: AgentInput) -> AgentOutput:
        """
        Execute agent with tracing.

        Args:
            agent_input: Structured input data

        Returns:
            Structured output with results and confidence
        """
        start_time = datetime.utcnow()
        step_number = len(self.traces) + 1
        trace = AgentTrace(
            agent_name=self.name,
            step_number=step_number,
            status=AgentStatus.RUNNING,
            input_data=agent_input.__dict__,
        )

        try:
            self.logger.info(
                f"Starting {self.name}",
                extra={
                    "agent": self.name,
                    "step": step_number,
                    "query": agent_input.query[:100],
                },
            )

            # Call the specialized agent implementation
            output = await self._execute(agent_input)

            # Update trace
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            trace.status = AgentStatus.SUCCESS
            trace.output_data = output.data
            trace.duration_ms = duration
            trace.metadata = output.metadata

            self.logger.info(
                f"Completed {self.name}",
                extra={
                    "agent": self.name,
                    "duration_ms": duration,
                    "confidence": output.confidence,
                },
            )

            self.traces.append(trace)
            return output

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = str(e)

            trace.status = AgentStatus.ERROR
            trace.error = error_msg
            trace.duration_ms = duration

            self.logger.error(
                f"Error in {self.name}: {error_msg}",
                extra={"agent": self.name, "error": error_msg},
                exc_info=True,
            )

            self.traces.append(trace)

            return AgentOutput(
                success=False,
                error=error_msg,
                confidence=0.0,
            )

    @abstractmethod
    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """
        Execute agent logic. Must be implemented by subclasses.

        Args:
            agent_input: Structured input data

        Returns:
            Agent output with results
        """
        pass

    def get_traces(self) -> List[AgentTrace]:
        """Get execution traces for this agent."""
        return self.traces

    def clear_traces(self):
        """Clear execution traces."""
        self.traces = []

    def __repr__(self) -> str:
        return f"<{self.name}: {self.description}>"
