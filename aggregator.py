import time

class Aggregator:
    def __init__(self, n_seconds=30):
        self.n_seconds=n_seconds
        self.last = time.time()
    def check(self):
        now = time.time()
        if (now - self.last)>self.n_seconds:
            self.last = now
            return True
        return False

        