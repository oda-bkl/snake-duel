from __future__ import annotations

from fastapi import APIRouter, Depends

from auth import get_current_user
from models import GameMode, ScoreEntry, SubmitScoreRequest, User
import store as st

router = APIRouter(prefix="/scores")


@router.post("", response_model=ScoreEntry)
def submit_score(body: SubmitScoreRequest, user: User = Depends(get_current_user)):
    return st.store.add_score(user, body.mode, body.score)


@router.get("/leaderboard", response_model=list[ScoreEntry])
def leaderboard(mode: GameMode, limit: int = 10):
    return st.store.leaderboard(mode, limit)
