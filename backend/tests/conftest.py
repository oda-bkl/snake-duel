"""Shared fixtures for all test modules."""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

pytest_plugins = ("anyio",)

from app.database import Base, engine, get_session, UserRow, TokenRow, ScoreRow, GameRow
from app.main import app
from app.security import hash_password
from app.store import UserRecord, store


@pytest.fixture(autouse=True, scope="session")
def setup_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def reset_store(setup_db):
    """Truncate all DB tables and reset SSE state before each test."""
    with get_session() as session:
        session.query(GameRow).delete()
        session.query(ScoreRow).delete()
        session.query(TokenRow).delete()
        session.query(UserRow).delete()
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
