import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, status

from app.config import settings
from app.core.deps import get_current_user
from app.models.user import User

_buckets: dict[int, deque] = defaultdict(deque)


def rate_limit_qa(user: User = Depends(get_current_user)):
    now = time.time()
    bucket = _buckets[user.id]
    while bucket and bucket[0] < now - 60:
        bucket.popleft()
    if len(bucket) >= settings.QA_RATE_LIMIT:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "提问过于频繁，请稍后再试")
    bucket.append(now)
    return user
