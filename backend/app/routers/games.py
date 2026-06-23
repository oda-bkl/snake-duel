import asyncio
import json
import time

from fastapi import APIRouter, Header
from fastapi.responses import Response, StreamingResponse

from ..auth import _extract_token
from ..models import ActiveGame, UpsertGameRequest
from ..store import store

router = APIRouter(tags=["games"])


def _now_ms() -> int:
    return int(time.time() * 1000)


@router.get("/games", response_model=list[ActiveGame])
async def list_active_games() -> list[ActiveGame]:
    return store.list_active_games()


# /games/stream must be declared before /games/{id} to avoid route shadowing
@router.get("/games/stream")
async def subscribe_active_games() -> StreamingResponse:
    async def generator():
        q = store.subscribe_global()
        try:
            games = store.list_active_games()
            yield f"data: {json.dumps([g.model_dump(mode='json') for g in games])}\n\n"
            while True:
                try:
                    games = await asyncio.wait_for(q.get(), timeout=25.0)
                    yield f"data: {json.dumps([g.model_dump(mode='json') for g in games])}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            store.unsubscribe_global(q)

    return StreamingResponse(generator(), media_type="text/event-stream")


@router.get("/games/{id}", response_model=ActiveGame | None)
async def get_active_game(id: str) -> ActiveGame | None:
    return store.get_game(id)


@router.put("/games/{id}", response_model=ActiveGame)
async def upsert_active_game(
    id: str,
    body: UpsertGameRequest,
    authorization: str | None = Header(default=None),
) -> ActiveGame:
    username = "guest"
    token = _extract_token(authorization)
    if token:
        record = store.get_user_by_token(token)
        if record:
            username = record.username

    game = ActiveGame(
        id=id,
        userId=body.userId,
        username=username,
        mode=body.mode,
        score=body.score,
        snake=body.snake,
        food=body.food,
        gridSize=body.gridSize,
        alive=body.alive,
        updatedAt=_now_ms(),
    )
    return store.upsert_game(game)


@router.delete("/games/{id}", status_code=204)
async def end_active_game(id: str) -> Response:
    game = store.get_game(id)
    if game is not None:
        ended = game.model_copy(update={"alive": False, "updatedAt": _now_ms()})
        store.upsert_game(ended)
        asyncio.get_event_loop().call_later(5.0, store.delete_game, id)
    return Response(status_code=204)


# /games/{id}/stream must come after /games/{id} but FastAPI matches exactly
@router.get("/games/{id}/stream")
async def subscribe_active_game(id: str) -> StreamingResponse:
    async def generator():
        q = store.subscribe_game(id)
        try:
            game = store.get_game(id)
            data = game.model_dump(mode='json') if game else None
            yield f"data: {json.dumps(data)}\n\n"
            while True:
                try:
                    game = await asyncio.wait_for(q.get(), timeout=25.0)
                    data = game.model_dump(mode='json') if game else None
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            store.unsubscribe_game(id, q)

    return StreamingResponse(generator(), media_type="text/event-stream")
