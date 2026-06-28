import time


class Metrics:
    def __init__(self):
        self.start = None

    def start_timer(self):
        self.start = time.time()

    def end_timer(self):
        return time.time() - self.start
