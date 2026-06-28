class BaseAgent:
    """
    All agents inherit from this structure
    """

    def run(self, input_data: dict):
        raise NotImplementedError("Agent must implement run()")
