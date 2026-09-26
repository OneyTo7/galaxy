from __future__ import annotations

import redis

from app.core.config import settings

_client = redis.Redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
QUEUE_KEY = "submission:queue"


def enqueue_submission(submission_id: int) -> None:
    if _client:
        _client.lpush(QUEUE_KEY, submission_id)


def consume_submission(timeout: int = 0) -> int | None:
    if not _client:
        return None
    item = _client.brpop(QUEUE_KEY, timeout=timeout)
    if item:
        _key, val = item
        return int(val)
    return None
