from time import monotonic


class QuotaManager:
    """
    Simple request-per-minute quota manager.
    APC architecture uses a global quota, not per-provider token budgets.
    """

    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.window_start = monotonic()
        self.count = 0

    def allowed(self) -> bool:
        now = monotonic()

        # Reset window every 60 seconds
        if now - self.window_start >= 60:
            self.window_start = now
            self.count = 0

        if self.count >= self.max_requests:
            return False

        self.count += 1
        return True
