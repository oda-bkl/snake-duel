"""Tests for games endpoints and SSE pub/sub."""

import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import ActiveGame, GameMode, Point
from app.store import store


GAME_BODY = {
    "id": "g_test1",
    "userId": "u_alice01",
    "mode": "walls",
    "score": 5,
    "snake": [{"x": 3, "y": 3}, {"x": 2, "y": 3}],
    "food": {"x": 7, "y": 7},
    "gridSize": 20,
    "alive": True,
}


def test_list_games_empty(client: TestClient):
    r = client.get("/api/games")
    assert r.status_code == 200
    assert r.json() == []


def test_upsert_and_list_game(client: TestClient, alice: dict):
    headers = {"Authorization": f"Bearer {alice['token']}"}
    r = client.put("/api/games/g_test1", json=GAME_BODY, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "g_test1"
    assert body["username"] == "alice"
    assert "updatedAt" in body

    games = client.get("/api/games").json()
    assert len(games) == 1
    assert games[0]["id"] == "g_test1"


def test_upsert_game_updates_existing(client: TestClient, alice: dict):
    headers = {"Authorization": f"Bearer {alice['token']}"}
    client.put("/api/games/g_test1", json=GAME_BODY, headers=headers)
    updated = {**GAME_BODY, "score": 10, "alive": False}
    r = client.put("/api/games/g_test1", json=updated, headers=headers)
    assert r.status_code == 200
    assert r.json()["score"] == 10
    assert r.json()["alive"] is False


def test_upsert_guest_game(client: TestClient):
    r = client.put("/api/games/g_guest", json={**GAME_BODY, "id": "g_guest", "userId": "guest"})
    assert r.status_code == 200
    assert r.json()["username"] == "guest"


def test_get_game_found(client: TestClient, alice: dict):
    headers = {"Authorization": f"Bearer {alice['token']}"}
    client.put("/api/games/g_test1", json=GAME_BODY, headers=headers)
    r = client.get("/api/games/g_test1")
    assert r.status_code == 200
    assert r.json()["id"] == "g_test1"


def test_get_game_not_found_returns_null(client: TestClient):
    r = client.get("/api/games/g_nope")
    assert r.status_code == 200
    assert r.json() is None


def test_end_game_sets_alive_false(client: TestClient, alice: dict):
    headers = {"Authorization": f"Bearer {alice['token']}"}
    client.put("/api/games/g_test1", json=GAME_BODY, headers=headers)
    r = client.delete("/api/games/g_test1")
    assert r.status_code == 204
    game = client.get("/api/games/g_test1").json()
    assert game is not None
    assert game["alive"] is False


def test_end_nonexistent_game(client: TestClient):
    r = client.delete("/api/games/g_nope")
    assert r.status_code == 204


def test_games_sorted_by_updated_at(client: TestClient, alice: dict):
    headers = {"Authorization": f"Bearer {alice['token']}"}
    client.put("/api/games/g_a", json={**GAME_BODY, "id": "g_a"}, headers=headers)
    client.put("/api/games/g_b", json={**GAME_BODY, "id": "g_b"}, headers=headers)
    games = client.get("/api/games").json()
    assert games[0]["updatedAt"] >= games[-1]["updatedAt"]


# ---------------------------------------------------------------------------
# SSE tests — call the ASGI app directly to avoid buffering in TestClient
# ---------------------------------------------------------------------------

async def _call_sse_endpoint(path: str, headers: list | None = None) -> dict:
    """
    Call an SSE endpoint directly via ASGI and collect the first body chunk.
    Returns {"status": int, "content_type": str, "first_event": str | None}.
    """
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": b"",
        "headers": headers or [],
        "root_path": "",
    }
    messages: list[dict] = []

    async def receive():
        await asyncio.sleep(100)  # never closes — SSE is long-lived
        return {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        messages.append(message)

    try:
        async with asyncio.timeout(2.0):
            await app(scope, receive, send)
    except TimeoutError:
        pass  # expected — SSE never ends

    status = next((m["status"] for m in messages if m["type"] == "http.response.start"), None)
    raw_headers = dict(
        next((m["headers"] for m in messages if m["type"] == "http.response.start"), [])
    )
    content_type = raw_headers.get(b"content-type", b"").decode()
    bodies = [m for m in messages if m["type"] == "http.response.body"]
    first_event = None
    for body_msg in bodies:
        text = body_msg["body"].decode()
        for line in text.split("\n"):
            if line.startswith("data: "):
                first_event = line[6:]
                break
        if first_event:
            break

    return {"status": status, "content_type": content_type, "first_event": first_event}


@pytest.mark.anyio
async def test_subscribe_active_games_sse_headers_and_data():
    result = await _call_sse_endpoint("/api/games/stream")
    assert result["status"] == 200
    assert "text/event-stream" in result["content_type"]
    assert result["first_event"] is not None
    data = json.loads(result["first_event"])
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_subscribe_active_games_sse_initial_data(alice: dict):
    """Upsert a game and check it appears in the initial SSE snapshot."""
    game = ActiveGame(
        id="g_test1", userId=alice["id"], username=alice["username"],
        mode=GameMode.walls, score=5,
        snake=[Point(x=3, y=3)], food=Point(x=7, y=7),
        gridSize=20, alive=True, updatedAt=1000,
    )
    store.games["g_test1"] = game  # bypass pub/sub

    result = await _call_sse_endpoint("/api/games/stream")
    data = json.loads(result["first_event"])
    assert len(data) == 1
    assert data[0]["id"] == "g_test1"


@pytest.mark.anyio
async def test_subscribe_single_game_sse_found(alice: dict):
    game = ActiveGame(
        id="g_test1", userId=alice["id"], username=alice["username"],
        mode=GameMode.walls, score=5,
        snake=[Point(x=3, y=3)], food=Point(x=7, y=7),
        gridSize=20, alive=True, updatedAt=1000,
    )
    store.games["g_test1"] = game

    result = await _call_sse_endpoint("/api/games/g_test1/stream")
    assert result["status"] == 200
    data = json.loads(result["first_event"])
    assert data["id"] == "g_test1"


@pytest.mark.anyio
async def test_subscribe_single_game_sse_not_found():
    result = await _call_sse_endpoint("/api/games/g_nope/stream")
    assert result["status"] == 200
    data = json.loads(result["first_event"])
    assert data is None


# ---------------------------------------------------------------------------
# Store pub/sub unit tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_store_global_pubsub_on_upsert(alice: dict):
    q = store.subscribe_global()
    try:
        game = ActiveGame(
            id="g_ps1", userId=alice["id"], username=alice["username"],
            mode=GameMode.walls, score=3,
            snake=[Point(x=1, y=1)], food=Point(x=5, y=5),
            gridSize=20, alive=True, updatedAt=1000,
        )
        store.upsert_game(game)
        update = q.get_nowait()
        assert any(g.id == "g_ps1" for g in update)
    finally:
        store.unsubscribe_global(q)


@pytest.mark.anyio
async def test_store_game_pubsub_on_upsert(alice: dict):
    q = store.subscribe_game("g_ps2")
    try:
        game = ActiveGame(
            id="g_ps2", userId=alice["id"], username=alice["username"],
            mode=GameMode.wrap, score=7,
            snake=[Point(x=2, y=2)], food=Point(x=6, y=6),
            gridSize=20, alive=True, updatedAt=2000,
        )
        store.upsert_game(game)
        update = q.get_nowait()
        assert update.id == "g_ps2"
    finally:
        store.unsubscribe_game("g_ps2", q)


@pytest.mark.anyio
async def test_store_global_pubsub_on_delete(alice: dict):
    game = ActiveGame(
        id="g_del", userId=alice["id"], username=alice["username"],
        mode=GameMode.walls, score=0,
        snake=[Point(x=0, y=0)], food=Point(x=1, y=1),
        gridSize=20, alive=True, updatedAt=3000,
    )
    store.games["g_del"] = game
    q = store.subscribe_global()
    try:
        store.delete_game("g_del")
        update = q.get_nowait()
        assert not any(g.id == "g_del" for g in update)
    finally:
        store.unsubscribe_global(q)
