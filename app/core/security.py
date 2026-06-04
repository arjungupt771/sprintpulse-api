from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import jwt
from pydantic import BaseModel

from app.core.config import get_settings


Scope = Literal["admin", "engineer"]


class TokenPayload(BaseModel):
    sub: str
    scopes: list[Scope]
    exp: int


def create_access_token(subject: str, scopes: list[Scope]) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "scopes": scopes, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

