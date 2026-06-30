from collections import defaultdict, deque
from time import time

from fastapi import HTTPException, Request, status

from app.core.config import get_settings


class RateLimiter:
    """Simple in-memory fixed-window limiter per client IP."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.window_seconds = 60
        self.records: dict[str, deque[float]] = defaultdict(deque)

    def check(self, request: Request) -> None:
        identifier = request.client.host if request.client else "unknown"
        now = time()
        queue = self.records[identifier]
        while queue and now - queue[0] > self.window_seconds:
            queue.popleft()
        if len(queue) >= self.settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        queue.append(now)
