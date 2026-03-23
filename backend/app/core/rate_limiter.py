"""Rate limiter for Gemini API calls - prevents 429 errors."""

import time
import threading
from collections import deque
from app.config import settings


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(
        self,
        max_per_minute: int = settings.GEMINI_REQUESTS_PER_MINUTE,
        max_per_day: int = settings.GEMINI_REQUESTS_PER_DAY,
    ):
        self.max_per_minute = max_per_minute
        self.max_per_day = max_per_day
        self._minute_calls: deque = deque()
        self._day_calls: deque = deque()
        self._lock = threading.Lock()

    def _cleanup(self):
        now = time.time()
        while self._minute_calls and now - self._minute_calls[0] > 60:
            self._minute_calls.popleft()
        while self._day_calls and now - self._day_calls[0] > 86400:
            self._day_calls.popleft()

    def wait_if_needed(self):
        """Block until a request slot is available."""
        while True:
            with self._lock:
                self._cleanup()
                if (
                    len(self._minute_calls) < self.max_per_minute
                    and len(self._day_calls) < self.max_per_day
                ):
                    now = time.time()
                    self._minute_calls.append(now)
                    self._day_calls.append(now)
                    return
            time.sleep(1)

    @property
    def remaining_minute(self) -> int:
        with self._lock:
            self._cleanup()
            return self.max_per_minute - len(self._minute_calls)

    @property
    def remaining_day(self) -> int:
        with self._lock:
            self._cleanup()
            return self.max_per_day - len(self._day_calls)


gemini_limiter = RateLimiter()
