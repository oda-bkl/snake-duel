import secrets
import time

from fastapi import APIRouter, Depends, Query

from ..auth import get_current_user
from ..models import GameMode, ScoreEntry, ScoreSubmitRequest
from ..store import UserRecord, store

router = APIRouter(tags=["scores"])


@router.post("/scores", status_code=201, response_model=ScoreEntry)
async def submit_score(
    body: ScoreSubmitRequest,
    user: UserRecord = Depends(get_current_user),
) -> ScoreEntry:
    entry = ScoreEntry(
        id="s_" + secrets.token_urlsafe(6),
        userId=user.id,
        username=user.username,
        mode=body.mode,
        score=body.score,
        createdAt=int(time.time() * 1000),
    )
    store.add_score(entry)
    return entry


@router.get("/leaderboard", response_model=list[ScoreEntry])
async def get_leaderboard(
    mode: GameMode = Query(...),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[ScoreEntry]:
    return store.get_leaderboard(mode, limit)
