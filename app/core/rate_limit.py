from uuid import UUID

import redis
from fastapi import Depends, HTTPException

from app.core.auth import get_current_owner_id
from app.core.config import get_settings

_redis_client = redis.Redis(
    host=get_settings().redis_host,
    port=get_settings().redis_port,
    decode_responses=True,
)

def rate_limiter(bucket_name: str, max_request: int, window_seconds: int):
    def dependency(owner_id: UUID = Depends(get_current_owner_id)) -> UUID:
        key = f"ratelimit:{bucket_name}:{owner_id}"
        count = _redis_client.incr(key)
        if count == 1:
            _redis_client.expire(key, window_seconds)
        if count > max_request:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later",
                headers={"Retry-After": str(window_seconds)}
            )
        return owner_id
    return dependency
