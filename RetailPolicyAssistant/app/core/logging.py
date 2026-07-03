import logging
import json
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "query"):
            log_data["query"] = record.query
        if hasattr(record, "route"):
            log_data["route"] = record.route
        if hasattr(record, "risk_level"):
            log_data["risk_level"] = record.risk_level
        if hasattr(record, "latency"):
            log_data["latency"] = record.latency
        if hasattr(record, "escalate"):
            log_data["escalate"] = record.escalate

        return json.dumps(log_data)


def setup_logging(log_dir: str = "logs", level: str = "INFO"):
    """
    Configure logging with file and console handlers.

    Args:
        log_dir: Directory for log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    formatter = JSONFormatter()

    file_handler = RotatingFileHandler(
        log_path / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    error_handler = RotatingFileHandler(
        log_path / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    audit_handler = RotatingFileHandler(
        log_path / "audit.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=20,
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(formatter)

    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(audit_handler)

    return root_logger


class AuditLogger:
    """Log audit events with structured data."""

    def __init__(self):
        self.logger = logging.getLogger("audit")

    def log_query(self, query: str, route: str, risk_level: str, escalate: bool, latency: float):
        """Log a query execution."""
        self.logger.info(
            f"Query executed: {query[:100]}...",
            extra={
                "query": query,
                "route": route,
                "risk_level": risk_level,
                "escalate": escalate,
                "latency": latency,
            },
        )

    def log_escalation(self, query: str, reason: str, risk_level: str):
        """Log an escalation event."""
        self.logger.warning(
            f"Escalation triggered: {reason}",
            extra={
                "query": query,
                "reason": reason,
                "risk_level": risk_level,
            },
        )

    def log_error(self, query: str, error: str, phase: str):
        """Log an error with context."""
        self.logger.error(
            f"Error in {phase}: {error}",
            extra={
                "query": query,
                "error": error,
                "phase": phase,
            },
        )

    def log_performance(self, component: str, latency: float, query_count: int = 1):
        """Log performance metrics."""
        self.logger.info(
            f"{component} latency: {latency:.3f}s",
            extra={
                "component": component,
                "latency": latency,
                "query_count": query_count,
            },
        )


class PerformanceTracker:
    """Track performance metrics."""

    def __init__(self):
        self.logger = logging.getLogger("performance")
        self.metrics = {}

    def record_latency(self, component: str, latency: float):
        """Record component latency."""
        if component not in self.metrics:
            self.metrics[component] = []
        self.metrics[component].append(latency)

    def get_stats(self, component: str):
        """Get latency statistics for component."""
        if component not in self.metrics or not self.metrics[component]:
            return None

        latencies = sorted(self.metrics[component])
        count = len(latencies)
        avg = sum(latencies) / count
        p95 = latencies[int(count * 0.95)]
        p99 = latencies[int(count * 0.99)]

        return {
            "component": component,
            "count": count,
            "avg": avg,
            "p95": p95,
            "p99": p99,
            "min": latencies[0],
            "max": latencies[-1],
        }

    def log_stats(self):
        """Log all statistics."""
        for component in self.metrics:
            stats = self.get_stats(component)
            if stats:
                self.logger.info(f"Performance Stats: {json.dumps(stats)}")


# Global instances
audit_logger = AuditLogger()
performance_tracker = PerformanceTracker()
