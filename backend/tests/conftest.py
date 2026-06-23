"""Shared fixtures for all test modules."""

import pytest
from fastapi.testclient import TestClient

pytest_plugins = ("anyio",)

from app.main import app
from app.store import Store, UserRecord, store
from app.security import hash_password


@pytest.fixture(autouse=True)
def reset_store():
    """Reset store to a clean empty state before each test."""
    store.users.clear()
    store._by_username.clear()
    store.tokens.clear()
    store.scores.clear()
    store.games.clear()
    store._global_subs.clear()
    store._game_subs.clear()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def alice(reset_store) -> dict:
    """Create alice and return {user_id, username, token}."""
    record = UserRecord(
        id="u_alice01",
        username="alice",
        password_hash=hash_password("pass123"),
    )
    store.add_user(record)
    token = store.create_token(record.id)
    return {"id": record.id, "username": record.username, "token": token}


@pytest.fixture
def auth_headers(alice) -> dict:
    return {"Authorization": f"Bearer {alice['token']}"}
