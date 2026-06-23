from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth import get_current_user
from models import AuthSession, LoginRequest, SignupRequest, User
import store as st

router = APIRouter(prefix="/auth")

_bearer = HTTPBearer(auto_error=False)


@router.post("/signup", response_model=AuthSession)
def signup(body: SignupRequest):
    try:
        user, token = st.store.create_user(body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return AuthSession(user=user, token=token)


@router.post("/login", response_model=AuthSession)
def login(body: LoginRequest):
    result = st.store.authenticate(body.username, body.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user, token = result
    return AuthSession(user=user, token=token)


@router.post("/logout", status_code=204)
def logout(
    _user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
):
    if creds:
        st.store.revoke_token(creds.credentials)
    return Response(status_code=204)


@router.get("/session")
def session(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    if creds is None:
        return None
    user = st.store.user_for_token(creds.credentials)
    if user is None:
        return None
    return AuthSession(user=user, token=creds.credentials)
