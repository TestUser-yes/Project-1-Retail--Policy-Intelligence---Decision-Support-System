import json
import time


class AgentLogger:
    """
    Lightweight observability layer for multi-agent system.
    """

    def __init__(self):
        self.logs = []

    def log(self, stage: str, data: dict):
        entry = {
            "stage": stage,
            "timestamp": time.time(),
            "data": data,
        }
        self.logs.append(entry)
        print(json.dumps(entry, indent=2))

    def get_logs(self):
        return self.logs
