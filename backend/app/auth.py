"""Password hashing and FastAPI auth dependencies."""

from fastapi import Header, HTTPException
from fastapi.security.utils import get_authorization_scheme_param

from .security import hash_password, verify_password
from .store import UserRecord, store


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer" or not token:
        return None
    return token


async def get_optional_user(
    authorization: str | None = Header(default=None),
) -> UserRecord | None:
    token = _extract_token(authorization)
    if not token:
        return None
    return store.get_user_by_token(token)


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> UserRecord:
    token = _extract_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = store.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


async def get_current_token(
    authorization: str | None = Header(default=None),
) -> str:
    token = _extract_token(authorization)
    if not token or store.get_user_by_token(token) is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token
