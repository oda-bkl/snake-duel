import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import Response

from ..auth import _extract_token, get_current_token
from ..security import hash_password, verify_password
from ..models import AuthSession, LoginRequest, SignupRequest
from ..store import UserRecord, store

router = APIRouter(tags=["auth"])


@router.post("/auth/signup", status_code=201, response_model=AuthSession)
async def signup(body: SignupRequest) -> AuthSession:
    if store.username_taken(body.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    uid = "u_" + secrets.token_urlsafe(6)
    record = UserRecord(
        id=uid,
        username=body.username,
        password_hash=hash_password(body.password),
    )
    store.add_user(record)
    token = store.create_token(uid)
    return AuthSession(user=record.to_user(), token=token)


@router.post("/auth/login", response_model=AuthSession)
async def login(body: LoginRequest) -> AuthSession:
    record = store.get_user_by_username(body.username)
    if record is None or not verify_password(body.password, record.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = store.create_token(record.id)
    return AuthSession(user=record.to_user(), token=token)


@router.post("/auth/logout", status_code=204)
async def logout(token: str = Depends(get_current_token)) -> Response:
    store.invalidate_token(token)
    return Response(status_code=204)


@router.get("/auth/session", response_model=AuthSession | None)
async def current_session(
    authorization: str | None = Header(default=None),
) -> AuthSession | None:
    token = _extract_token(authorization)
    if not token:
        return None
    record = store.get_user_by_token(token)
    if record is None:
        return None
    return AuthSession(user=record.to_user(), token=token)
