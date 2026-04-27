from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.auth import TokenPayload


def create_access_token(
    *,
    user_id: str,
    username: str,
    roles: list[str],
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.app_access_token_expire_minutes)
    )
    payload = {
        "sub": user_id,
        "username": username,
        "roles": roles,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        payload,
        settings.app_jwt_secret,
        algorithm=settings.app_jwt_algorithm,
    )
    return encoded_jwt, int(expire.timestamp())


def decode_access_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.app_jwt_secret,
            algorithms=[settings.app_jwt_algorithm],
        )
        return TokenPayload.model_validate(payload)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        ) from exc

