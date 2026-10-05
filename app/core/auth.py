from uuid import UUID

import jwt
from fastapi import Header, HTTPException

from app.core.config import get_settings


def get_current_owner_id(authorization: str | None = Header(default=None)) -> UUID:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth header")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")