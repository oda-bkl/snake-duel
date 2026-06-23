from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from auth import get_current_user
from models import ActiveGame, UpsertGameRequest, User
import store as st

router = APIRouter(prefix="/games")


@router.get("/active", response_model=list[ActiveGame])
def list_active():
    return st.store.list_games()


@router.post("/active", response_model=ActiveGame)
def upsert_game(body: UpsertGameRequest, user: User = Depends(get_current_user)):
    data = body.model_dump(exclude={"id", "userId"})
    return st.store.upsert_game(user, body.id, data)


@router.get("/active/{gid}")
def get_active(gid: str):
    return st.store.get_game(gid)


@router.post("/active/{gid}/end", status_code=204)
def end_game(gid: str, _user: User = Depends(get_current_user)):
    if not st.store.end_game(gid):
        raise HTTPException(status_code=404, detail="Game not found")
    return Response(status_code=204)
